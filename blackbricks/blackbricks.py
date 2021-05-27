import itertools
from dataclasses import dataclass
from typing import Iterator

import black
import sqlparse
from black.nodes import is_docstring, is_multiline_string
from black.strings import fix_docstring
from blib2to3.pytree import Leaf

_black_default_str = black.Line.__str__
_black_default_visit_string = black.LineGenerator.visit_STRING

COMMAND = "# COMMAND ----------"
HEADER = "# Databricks notebook source"
NOFMT = "-- nofmt"
CELL_TITLE = "# DBTITLE 1,"


@dataclass(frozen=True)
class FormatConfig:
    "Data-only class to hold format configuration options and their defaults."
    line_length: int = black.DEFAULT_LINE_LENGTH
    sql_upper: bool = True
    two_space_indent: bool = True


def _make_black_use_two_spaces(do_it: bool) -> None:
    """Force black to use two spaces for indentation.

    This is a copy of:

    `black.Line.__str__` with only one change:
        indent = "  " * self.depth

    `black.LineGenerator.visit_STRING` with only one change:
        indent = " " * 2 * self.current_line.depth

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

    def patch_visit_STRING(self, leaf: Leaf) -> Iterator[black.Line]:
        if is_docstring(leaf) and "\\\n" not in leaf.value:
            # We're ignoring docstrings with backslash newline escapes because changing
            # indentation of those changes the AST representation of the code.
            prefix = black.strings.get_string_prefix(leaf.value)
            docstring = leaf.value[len(prefix) :]  # Remove the prefix
            quote_char = docstring[0]
            # A natural way to remove the outer quotes is to do:
            #   docstring = docstring.strip(quote_char)
            # but that breaks on """""x""" (which is '""x').
            # So we actually need to remove the first character and the next two
            # characters but only if they are the same as the first.
            quote_len = 1 if docstring[1] != quote_char else 3
            docstring = docstring[quote_len:-quote_len]
            docstring_started_empty = not docstring

            if is_multiline_string(leaf):
                indent = " " * 2 * self.current_line.depth
                docstring = fix_docstring(docstring, indent)
            else:
                docstring = docstring.strip()

            if docstring:
                # Add some padding if the docstring starts / ends with a quote mark.
                if docstring[0] == quote_char:
                    docstring = " " + docstring
                if docstring[-1] == quote_char:
                    docstring += " "
                if docstring[-1] == "\\":
                    backslash_count = len(docstring) - len(docstring.rstrip("\\"))
                    if backslash_count % 2:
                        # Odd number of tailing backslashes, add some padding to
                        # avoid escaping the closing string quote.
                        docstring += " "
            elif not docstring_started_empty:
                docstring = " "

            # We could enforce triple quotes at this point.
            quote = quote_char * quote_len
            leaf.value = prefix + quote + docstring + quote

        yield from self.visit_default(leaf)

    if do_it:
        black.Line.__str__ = patch
        black.LineGenerator.visit_STRING = patch_visit_STRING
    else:
        black.Line.__str__ = _black_default_str
        black.LineGenerator.visit_STRING = _black_default_visit_string


def format_str(content: str, config: FormatConfig = FormatConfig()) -> str:
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


def _format_sql_cell(cell: str, sql_keyword_case: str = "upper") -> str:
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

    magics = []
    sql_lines = []
    for line in cell.strip().splitlines():
        if line.strip().startswith("# MAGIC %sql"):
            continue
        words = line.split()
        magic, sql = words[:2], words[2:]
        magics.append(magic)
        sql_lines.append(" ".join(sql).strip())

    return (
        title_line
        + "# MAGIC %sql\n"
        + "\n".join(
            f"# MAGIC {sql}"
            for sql in sqlparse.format(
                "\n".join(sql_lines), reindent=True, keyword_case=sql_keyword_case
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
