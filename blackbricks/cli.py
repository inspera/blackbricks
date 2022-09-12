import os
import textwrap
import warnings
from typing import List, NoReturn, Optional, Sequence

import black
import typer

from . import __version__
from .blackbricks import HEADER, FormatConfig, format_str, unified_diff
from .databricks_sync import get_api_client
from .files import (
    File,
    LocalFile,
    RemoteNotebook,
    resolve_databricks_paths,
    resolve_filepaths,
)

app = typer.Typer(add_completion=False)


def process_files(
    files: Sequence[File],
    format_config: FormatConfig = FormatConfig(),
    diff: bool = False,
    check: bool = False,
) -> int:
    no_change = True
    n_changed_files = 0
    n_notebooks = 0

    for file_ in files:

        try:
            content = file_.content
        except UnicodeDecodeError:
            # File is not a text file. Probably a binary file. Skip.
            continue

        if not content.lstrip() or HEADER not in content.lstrip().splitlines()[0]:
            # Not a Databricks notebook - skip
            continue

        n_notebooks += 1
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
            file_.content = output

            if output != content:
                typer.secho(f"reformatted {file_.path}", bold=True)
        elif check and output != content:
            typer.secho(f"would reformat {file_.path}", bold=True)

    unchanged_number = typer.style(
        str(n_notebooks - n_changed_files), fg=typer.colors.GREEN
    )
    changed_number = typer.style(str(n_changed_files), fg=typer.colors.MAGENTA)
    unchanged_echo = (
        f"{unchanged_number} files {'would be ' if check or diff else ''}left unchanged"
    )
    changed_echo = typer.style(
        f"{changed_number} files {'would be ' if check or diff else ''}reformatted",
        bold=True,
    )

    typer.secho("All done!", bold=True)
    typer.echo(
        ", ".join(
            filter(
                lambda s: bool(s),
                [
                    changed_echo if n_changed_files else "",
                    unchanged_echo if n_notebooks - n_changed_files > 0 else "",
                ],
            )
        )
    )
    return n_changed_files


def mutually_exclusive(names: List[str], values: List[bool]) -> None:
    if sum(values) > 1:
        names_formatted = ", ".join(
            typer.style(name, fg=typer.colors.CYAN) for name in names
        )
        typer.echo(
            f"{typer.style('Error:', fg=typer.colors.RED)} "
            + f"Only one of {names_formatted} may be use at the same time."
        )
        raise typer.Exit(1)


def version_callback(version_requested: bool) -> None:
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
        black.const.DEFAULT_LINE_LENGTH, help="How many characters per line to allow."
    ),
    sql_upper: bool = typer.Option(
        True, help="SQL keywords should be UPPERCASE or lowercase."
    ),
    no_indent_with_two_spaces: Optional[bool] = typer.Option(
        None,
        "--no-indent-with-two-spaces",
        help="DEPRECATED: Blackbricks now uses 4 spaces for indentation by default. This option will be removed in future versions.",
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
) -> NoReturn:
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
    assert not version, "If version is set, we don't get here."

    if no_indent_with_two_spaces is not None:
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn(
            textwrap.dedent(
                """
                Blackbricks now uses 4 spaces for indentation by default.
                Please stop using the `--no-indent-with-two-spaces` option, as it will be removed in future versions.
                """
            ),
            category=DeprecationWarning,
            stacklevel=0,
        )

    mutually_exclusive(["--check", "--diff"], [check, diff])

    if not filenames:
        typer.secho("No Path provided. Nothing to do.", bold=True)
        raise typer.Exit()

    files: List[File]
    if remote_filenames:
        api_client = get_api_client(databricks_profile)
        files = [
            RemoteNotebook(fname, api_client)
            for fname in resolve_databricks_paths(filenames, api_client=api_client)
        ]
    else:
        files = [LocalFile(fname) for fname in resolve_filepaths(filenames)]

    n_changed_files = process_files(
        files,
        format_config=FormatConfig(line_length=line_length, sql_upper=sql_upper),
        diff=diff,
        check=check,
    )
    raise typer.Exit(n_changed_files if check else 0)


if __name__ == "__main__":
    app()
