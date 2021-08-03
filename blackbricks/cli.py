import os
from typing import List, Sequence

import black
import typer

from . import __version__
from .blackbricks import HEADER, FormatConfig, format_str, unified_diff
from .databricks_sync import get_api_client
from .files import File, LocalFile, RemoteNotebook, resolve_filepaths

app = typer.Typer(add_completion=False)


def process_files(
    files: Sequence[File],
    format_config: FormatConfig = FormatConfig(),
    diff: bool = False,
    check: bool = False,
):
    no_change = True
    n_changed_files = 0

    for file_ in files:
        content = file_.content

        if not content.lstrip() or HEADER not in content.lstrip().splitlines()[0]:
            # Not a Databricks notebook - skip
            continue

        output = format_str(content, config=format_config)

        no_change &= output == content
        n_changed_files += output != content

        if diff:
            diff_output = unified_diff(
                content,
                output,
                f"{os.path.basename(file_.path)} (before)",
                f"{os.path.basename(file_.path)} (after)",
            )
            if diff_output.strip():
                typer.echo(diff_output)
        elif not check:
            out_str = ""
            for line in output.splitlines():
                out_str += line.rstrip() + "\n"
            file_.content = out_str

            if output != content:
                typer.secho(f"reformatted {file_.path}", bold=True)
        elif check and output != content:
            typer.secho(f"would reformat {file_.path}", bold=True)

    unchanged_number = typer.style(
        str(len(files) - n_changed_files), fg=typer.colors.GREEN
    )
    changed_number = typer.style(str(n_changed_files), fg=typer.colors.MAGENTA)
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
                    unchanged_echo if len(files) - n_changed_files > 0 else "",
                ],
            )
        )
    )
    return n_changed_files


def mutually_exclusive(names, values):
    if sum(values) > 1:
        names = ", ".join(typer.style(name, fg=typer.colors.CYAN) for name in names)
        typer.echo(
            f"{typer.style('Error:', fg=typer.colors.RED)} "
            + f"Only one of {names} may be use at the same time."
        )
        raise typer.Exit(1)


def version_callback(version_requested: bool):
    "Display versioin information and exit"
    if version_requested:
        version = typer.style(__version__, fg=typer.colors.GREEN)
        typer.echo(f"blackbricks, version {version}")
        raise typer.Exit()


@app.command()
def main(
    filenames: List[str] = typer.Argument(
        None, help="Path to the notebook(s) to format."
    ),
    remote_filenames: bool = typer.Option(
        False,
        "--remote",
        "-r",
        help="If this option is used, all filenames are treated as paths to "
        "notebooks on your Databricks host (i.e. not local files).",
    ),
    databricks_profile: str = typer.Option(
        "DEFAULT",
        "--profile",
        "-p",
        metavar="NAME",
        help="If using --remote, which Databricks profile to use.",
    ),
    line_length: int = typer.Option(
        black.DEFAULT_LINE_LENGTH, help="How many characters per line to allow."
    ),
    sql_upper: bool = typer.Option(
        True, help="SQL keywords should be UPPERCASE or lowercase."
    ),
    indent_with_two_spaces: bool = typer.Option(
        True,
        help="Use two spaces for indentation in Python cells instead of Black's "
        "default of four. Databricks uses two spaces.",
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

    Local files (without the `--remote` option):

      - Only files that look like Databricks (Python) notebooks will be processed. That is, they must start with the header `# Databricks notebook source`

      - If you specify a directory as one of the file names, all files in that directory will be added, including any subdirectory.

    Remote files (with the `--remote` option):

      - Make sure you have installed the Databricks CLI (``pip install databricks_cli``)

      - Make sure you have configured at least one profile (`databricks configure`). Check the file `~/.databrickscfg` if you are not sure.

      - File paths should start with `/`. Otherwise they are interpreted as relative to `/Users/username`, where `username` is the username specified in the Databricks profile used.
    """

    mutually_exclusive(["--check", "--diff"], [check, diff])

    if not filenames:
        typer.secho("No Path provided. Nothing to do.", bold=True)
        raise typer.Exit()

    if remote_filenames:
        api_client = get_api_client(databricks_profile)
        files = [RemoteNotebook(fname, api_client) for fname in filenames]
    else:
        files = [LocalFile(fname) for fname in resolve_filepaths(filenames)]

    n_changed_files = process_files(
        files,
        format_config=FormatConfig(
            line_length=line_length,
            sql_upper=sql_upper,
            two_space_indent=indent_with_two_spaces,
        ),
        diff=diff,
        check=check,
    )
    raise typer.Exit(n_changed_files if check else 0)


if __name__ == "__main__":
    app()
