"""
Formatting tool for Databricks python notebooks.

Python cells are formatted using `black`, and SQL cells are formatted by `sqlparse`.
"""
import itertools
import os
from typing import List, Tuple

import black
import sqlparse
import typer

from . import __version__


app = typer.Typer(add_completion=False)


def make_black_use_two_spaces(do_it: bool):
    """Force black to use two spaces for indentation.

    This is a copy of `black.Line.__str__` with only one change:
        indent = "  " * self.depth
    I.e. changing the indentation used.

    Change only applied if `do_it` is True.
    """

    def patch(self) -> str:
        """Render the line."""
        if not self:
            return "\n"

        indent = "  " * self.depth
        leaves = iter(self.leaves)
        first = next(leaves)
        res = f"{first.prefix}{indent}{first.value}"
        for leaf in leaves:
            res += str(leaf)
        for comment in itertools.chain.from_iterable(self.comments.values()):
            res += str(comment)
        return res + "\n"

    if do_it:
        black.Line.__str__ = patch


def infinite_magic():
    while True:
        yield "# MAGIC "


def format_sql_cell(cell, sql_keyword_case="upper"):
    magics = []
    sql_lines = []
    for line in cell.strip().splitlines():
        if line.strip().startswith("# MAGIC %sql"):
            continue
        words = line.split()
        magic, sql = words[:2], words[2:]
        magics.append(magic)
        sql_lines.append(" ".join(sql).strip())

    return "# MAGIC %sql\n" + "\n".join(
        f"{magic}{sql}"
        for magic, sql in zip(
            infinite_magic(),
            sqlparse.format(
                "\n".join(sql_lines), reindent=True, keyword_case=sql_keyword_case
            ).splitlines(),
        )
    )


def unified_diff(a, b, a_name, b_name):
    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line + "\n" for line in a.split("\n")]
    b_lines = [line + "\n" for line in b.split("\n")]
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5)
    )


def version_callback(version_requested: bool):
    if version_requested:
        version = typer.style(__version__, fg=typer.colors.GREEN)
        typer.echo(f"blackbricks, version {version}")
        raise typer.Exit()


def filenames_callback(paths: Tuple[str]):
    """Resolve the paths given into valid file names

    Directories are recursively added, similarly to how black operates.
    """
    paths = list(paths)
    file_paths = []
    while paths:
        path = os.path.abspath(paths.pop())

        if not os.path.exists(path):
            typer.echo(
                typer.style("Error:", fg=typer.colors.RED)
                + " No such file or directory: "
                + typer.style(path, fg=typer.colors.CYAN)
            )
            raise typer.Exit(1)

        if os.path.isdir(path):

            # Recursively  add all the files/dirs in path to the paths to be consumed.
            paths.extend([os.path.join(path, f) for f in os.listdir(path)])

        else:

            file_paths.append(path)

    return file_paths


def mutually_exclusive(names, values):
    if sum(values) > 1:
        names = ", ".join(typer.style(name, fg=typer.colors.CYAN) for name in names)
        typer.echo(
            f"{typer.style('Error:', fg=typer.colors.RED)} "
            + f"Only one of {names} may be use at the same time."
        )
        raise typer.Exit(1)


@app.command()
def main(
    filenames: List[str] = typer.Argument(
        None, callback=filenames_callback, help="Path to the notebook(s) to format.",
    ),
    line_length: int = typer.Option(
        black.DEFAULT_LINE_LENGTH, help="How many characters per line to allow."
    ),
    sql_upper: bool = typer.Option(
        True, "--sql-upper", help="SQL keywords should be UPPERCASE."
    ),
    sql_lower: bool = typer.Option(
        False, "--sql-lower", help="SQL keywords should be lowercase."
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Don't write the files back, just return the status. "
        "Return code 0 means nothing would change.",
        show_default=False,
    ),
    diff: bool = typer.Option(
        False,
        "--diff",
        help="Don't write the files back, just output a diff for each file on stdout.",
        show_default=False,
    ),
    indent_with_two_spaces: bool = typer.Option(
        True,
        callback=make_black_use_two_spaces,
        help="Use two spaces for indentation in Python cells instead of Black's "
        "default of four. Databricks uses two spaces.",
    ),
    version: bool = typer.Option(
        None,
        "--version",
        is_eager=True,
        callback=version_callback,
        help="Display version information and exit.",
    ),
):
    """
    Formatting tool for Databricks python notebooks.

    Python cells are formatted using `black`, and SQL cells are formatted by `sqlparse`.
    """

    mutually_exclusive(["--sql-upper", "--sql-lower"], [sql_upper, sql_lower])
    mutually_exclusive(["--check", "--diff"], [check, diff])

    if not filenames:
        typer.secho("No Path provided. Nothing to do.", bold=True)
        raise typer.Exit()

    no_change = True
    n_changed_files = 0
    for filename in filenames:
        with open(filename) as f:
            content = f.read()

        COMMAND = "# COMMAND ----------"
        HEADER = "# Databricks notebook source"

        if HEADER not in content.lstrip().splitlines()[0]:
            # Note a Databricks notebook - skip
            continue

        cells = content.replace(HEADER, "", 1).split(COMMAND)

        output_cells = []
        for cell in cells:
            cell = cell.strip()

            if "# MAGIC %sql" in cell:
                output_cells.append(
                    format_sql_cell(
                        cell, sql_keyword_case="lower" if sql_lower else "upper"
                    )
                )
            elif "# MAGIC" in cell:
                output_cells.append(cell)  # Generic magic cell - output as-is.
            else:
                output_cells.append(
                    black.format_str(cell, mode=black.FileMode(line_length=line_length))
                )

        output = (
            f"{HEADER}\n"
            + f"\n\n{COMMAND}\n\n".join(
                "".join(line.rstrip() + "\n" for line in cell.splitlines()).rstrip()
                for cell in output_cells
            ).rstrip()
            + "\n"
        )

        no_change &= output == content
        n_changed_files += output != content

        if diff:
            diff_output = unified_diff(
                content,
                output,
                f"{os.path.basename(filename)} (before)",
                f"{os.path.basename(filename)} (after)",
            )
            if diff_output.strip():
                typer.echo(diff_output)
        elif not check:
            with open(filename, "w") as f:
                for line in output.splitlines():
                    f.write(line.rstrip() + "\n")

            if output != content:
                typer.secho(f"reformatted {filename}", bold=True)
        elif check and output != content:
            typer.secho(f"would reformat {filename}", bold=True)

    unchanged_number = typer.style(
        str(len(filenames) - n_changed_files), fg=typer.colors.GREEN
    )
    changed_number = typer.style(str(n_changed_files), fg=typer.colors.RED)
    unchanged_echo = (
        f"{unchanged_number} files {'would be ' if check else ''}left unchanged"
    )
    changed_echo = typer.style(
        f"{changed_number} files {'would be ' if check else ''}reformatted", bold=True
    )

    typer.secho("All done!", bold=True)
    typer.echo(
        ", ".join(
            filter(
                lambda s: bool(s),
                [
                    changed_echo if n_changed_files else "",
                    unchanged_echo if len(filenames) - n_changed_files > 0 else "",
                ],
            )
        )
    )

    raise typer.Exit(n_changed_files if check else 0)


if __name__ == "__main__":
    app()
