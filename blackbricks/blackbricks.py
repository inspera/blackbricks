"""
Formatting tool for Databricks python notebooks.

Python cells are formatted using `black`, and SQL cells are formatted by `sqlparse`.
"""
import argparse
import os
import sys
from typing import List, Optional

import black
import sqlparse
import typer

from . import __version__

app = typer.Typer(add_completion=False)


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


def fix_indentation_level(cell, use_two_spaces=False):
    if not use_two_spaces:
        # Assumed that Black has already done its thing and indentation is OK with four spaces.
        return cell

    reindented = []
    for line in cell.splitlines():
        n_spaces = 0
        for char in line:
            if char != " ":
                break
            n_spaces += 1

        if n_spaces % 4 != 0:
            # Unknown indent level, probably inside a multiline string. Don't change.
            reindented.append(line)
        else:
            reindented.append(" " * (n_spaces // 2) + line[n_spaces:])

    return "\n".join(reindented)


def version_callback(version_requested: bool):
    if version_requested:
        version = typer.style(__version__, fg=typer.colors.GREEN)
        typer.echo(f"blackbricks, version {version}")
        raise typer.Exit()


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
        None,
        path_type=str,
        exists=True,
        resolve_path=True,
        help="Path to the notebook(s) to format.",
    ),
    line_length: int = typer.Option(
        black.DEFAULT_LINE_LENGTH, help="How many characters per line to allow."
    ),
    sql_upper: bool = typer.Option(
        False, "--sql-upper", help="SQL keywords should be UPPERCASE."
    ),
    sql_lower: bool = typer.Option(
        False, "--sql-lower", help="SQL keywords should be lowercase."
    ),
    check: bool = typer.Option(
        False,
        "--check",
        help="Don't write the files back, just return the status. Return code 0 means nothing would change.",
        show_default=False,
    ),
    diff: bool = typer.Option(
        False,
        "--diff",
        help="Don't write the files back, just output a diff for each file on stdout.",
        show_default=False,
    ),
    indent_with_two_spaces: bool = typer.Option(
        False,
        "--indent-with-two-spaces",
        help="Use two spaces for indentation in Python cells instead of Black's default of four.",
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

    # Validate file paths:
    for filename in filenames:
        try:
            with open(filename) as f:
                pass
        except FileNotFoundError:
            typer.echo(
                typer.style("Error:", fg=typer.colors.RED)
                + " No such file or directory: "
                + typer.style(filename, fg=typer.colors.CYAN)
            )
            raise typer.Exit(1)

    no_change = True
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
                    fix_indentation_level(
                        black.format_str(
                            cell, mode=black.FileMode(line_length=line_length)
                        ),
                        indent_with_two_spaces,
                    )
                )

        output = (
            f"{HEADER}\n\n"
            + f"\n\n{COMMAND}\n\n".join(
                "".join(line.rstrip() + "\n" for line in cell.splitlines()).rstrip()
                for cell in output_cells
            ).rstrip()
            + "\n"
        )

        no_change &= output == content

        if diff:
            print(
                unified_diff(
                    content,
                    output,
                    f"{os.path.basename(filename)} (before)",
                    f"{os.path.basename(filename)} (after)",
                )
            )
        elif not check:
            with open(filename, "w") as f:
                for line in output.splitlines():
                    f.write(line.rstrip() + "\n")

    raise typer.Exit(int(not no_change) if check else 0)


if __name__ == "__main__":
    app()
