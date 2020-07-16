import itertools
from dataclasses import dataclass

import black
import sqlparse

_black_default_str = black.Line.__str__


COMMAND = "# COMMAND ----------"
HEADER = "# Databricks notebook source"


@dataclass(frozen=True)
class FormatConfig:
    line_length: int = black.DEFAULT_LINE_LENGTH
    sql_upper: bool = True
    two_space_indent: bool = True


def _make_black_use_two_spaces(do_it: bool):
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
    else:
        black.Line.__str__ = _black_default_str


def format_str(content: str, config: FormatConfig = FormatConfig()):
    """
    Format the content of a notebook according to the format config provided.

    This assumes that `content` is the _full_ content of a notebook file, and that
    the notebook is a Python notebook.

    :param content: A string holding the entire content of a notebook.
    :param config: An object holding the desired formatting options.
    :return: The content of the file, formatted according to the configuration.
    """
    _make_black_use_two_spaces(config.two_space_indent)

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
        + "\n"
    )

    return output


def _format_sql_cell(cell, sql_keyword_case="upper"):
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
        f"# MAGIC {sql}"
        for sql in sqlparse.format(
            "\n".join(sql_lines), reindent=True, keyword_case=sql_keyword_case
        ).splitlines()
    )


def unified_diff(a, b, a_name, b_name):
    """Return a unified diff string between strings `a` and `b`."""
    import difflib

    a_lines = [line + "\n" for line in a.split("\n")]
    b_lines = [line + "\n" for line in b.split("\n")]
    return "".join(
        difflib.unified_diff(a_lines, b_lines, fromfile=a_name, tofile=b_name, n=5)
    )
