from dataclasses import dataclass
from typing import Literal, Union

import black
import sqlparse

COMMAND = "# COMMAND ----------"
HEADER = "# Databricks notebook source"
NOFMT = "-- nofmt"
CELL_TITLE = "# DBTITLE 1,"


@dataclass(frozen=True)
class FormatConfig:
    "Data-only class to hold format configuration options and their defaults."
    line_length: int = black.const.DEFAULT_LINE_LENGTH
    sql_upper: bool = True


def format_str(content: str, config: FormatConfig = FormatConfig()) -> str:
    """
    Format the content of a notebook according to the format config provided.

    This assumes that `content` is the _full_ content of a notebook file, and that
    the notebook is a Python notebook.

    :param content: A string holding the entire content of a notebook.
    :param config: An object holding the desired formatting options.
    :return: The content of the file, formatted according to the configuration.
    """
    cells = content.replace(HEADER, "", 1).split(COMMAND)

    output_cells = []
    for cell in cells:
        cell = cell.strip()

        if "# MAGIC %sql" in cell:
            output_cells.append(
                _format_sql_cell(
                    cell, sql_keyword_case="upper" if config.sql_upper else "lower"
                )
            )
        elif "# MAGIC" in cell:
            output_cells.append(cell)  # Generic magic cell - output as-is.
        else:
            output_cells.append(
                black.format_str(
                    cell, mode=black.FileMode(line_length=config.line_length)
                )
            )

    output = (
        f"{HEADER}\n"
        + f"\n\n{COMMAND}\n\n".join(
            "".join(line.rstrip() + "\n" for line in cell.splitlines()).rstrip()
            for cell in output_cells
        ).rstrip()
    )

    # Databricks adds a space after '# MAGIC', regardless of wheter this constitutes
    # trailing whitespace. To avoid perpetual differences, blackbricks also adds this
    # extra whitespace. This is only added if the line does not contain anything else.
    # In all other cases, blackbricks will remove trailing whitespace.
    output_ws_normalized = ""
    for line in output.splitlines():
        line = line.rstrip()

        if line == "# MAGIC":
            line += " "

        output_ws_normalized += line + "\n"

    return output_ws_normalized.strip()


def _format_sql_cell(
    cell: str, sql_keyword_case: Union[Literal["upper"], Literal["lower"]] = "upper"
) -> str:
    """
    Format a MAGIC %sql cell.

    :param cell: The content of an SQL cell.
    :param sql_keyword_case: One of ["upper", "lower"], setting the case for SQL keywords.
    :return: The cell with formatting applied.
    """

    # Cells can have a title. This should just be kept at the start of the cell.
    if CELL_TITLE in cell.lstrip().splitlines()[0]:
        title_line = cell.lstrip().splitlines()[0] + "\n"
        cell = cell[len(title_line) :]
    else:
        title_line = ""

    # Formatting can be disabled on a cell-by-cell basis by adding `-- nofmt` to the first line.
    if NOFMT in cell.strip().splitlines()[0]:
        return title_line + cell

    sql_lines = []
    for line in (line.strip() for line in cell.strip().splitlines()):
        if line == "# MAGIC %sql":
            continue
        elif line.startswith("# MAGIC %sql"):
            line = line.replace(" %sql", "", 1)
        sql = line.split()[2:]  # Remove "# MAGIC".
        sql_lines.append(" ".join(sql).strip())

    return (
        title_line
        + "# MAGIC %sql\n"
        + "\n".join(
            f"# MAGIC {sql}"
            for sql in sqlparse.format(
                "\n".join(sql_lines).strip(),
                reindent=True,
                keyword_case=sql_keyword_case,
            ).splitlines()
        )
    )


def unified_diff(a: str, b: str, a_name: str, b_name: str) -> str:
    """
    Return a unified diff string between strings `a` and `b`.

    :param a: The first string (e.g. before).
    :param b: The second string (e.g. after).
    :param a_name: The "filename" to display for the `a` string.
    :param b_name: The "filename" to display for the `b` string.
    :return: A `git diff` like diff of the two strings.
    """
    import difflib

    a_lines = [line + "\n" for line in a.split("\n")]
    b_lines = [line + "\n" for line in b.split("\n")]
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5)
    )
