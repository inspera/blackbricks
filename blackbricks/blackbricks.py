"""
Formatting tool for Databricks python notebooks.

Python cells are formatted using `black`, and SQL cells are formatted by `sqlparse`.
"""
import argparse
import os
import sys

import black
import sqlparse

from . import __version__


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


def validate_filenames(path):
    path = os.path.abspath(path)
    try:
        with open(path):
            return path
    except IOError:
        raise argparse.ArgumentTypeError(f"Could not open file: {path}") from None


def diff(a, b, a_name, b_name):
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "filenames",
        nargs="*",
        type=validate_filenames,
        help="Path to the notebook(s) to format",
    )
    parser.add_argument(
        "--line-length",
        type=int,
        default=black.DEFAULT_LINE_LENGTH,
        help="How many characters per line to allow. [default: ask black]",
    )
    sql_case_group = parser.add_mutually_exclusive_group()
    sql_case_group.add_argument(
        "--sql-upper",
        action="store_true",
        default=True,
        help="SQL keywords should be uppercase",
    )
    sql_case_group.add_argument(
        "--sql-lower", action="store_true", help="SQL keywords should be lowercase"
    )

    result_group = parser.add_mutually_exclusive_group()
    result_group.add_argument(
        "--check",
        action="store_true",
        help="Don't write the files back, just return the status. Return code 0 means nothing would change.",
    )
    result_group.add_argument(
        "--diff",
        action="store_true",
        help="Don't write the files back, just output a diff for each file on stdout",
    )

    parser.add_argument(
        "--indent-with-two-spaces",
        action="store_true",
        help="Use two spaces for indentation in Python cells instead of Black's default of four.",
    )

    parser.add_argument(
        "--version", action="store_true", help="Display version information and exit."
    )

    args = parser.parse_args()

    if args.version:
        print(f"blackbricks, version {__version__}")
        sys.exit(0)

    no_change = True

    for filename in args.filenames:
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
                        cell, sql_keyword_case="lower" if args.sql_lower else "upper"
                    )
                )
            elif "# MAGIC" in cell:
                output_cells.append(cell)  # Generic magic cell - output as-is.
            else:
                output_cells.append(
                    fix_indentation_level(
                        black.format_str(
                            cell, mode=black.FileMode(line_length=args.line_length)
                        ),
                        args.indent_with_two_spaces,
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

        if args.diff:
            print(
                diff(
                    content,
                    output,
                    f"{os.path.basename(filename)} (before)",
                    f"{os.path.basename(filename)} (after)",
                )
            )
        elif not args.check:
            with open(filename, "w") as f:
                for line in output.splitlines():
                    f.write(line.rstrip() + "\n")

    sys.exit(int(not no_change))


if __name__ == "__main__":
    main()
