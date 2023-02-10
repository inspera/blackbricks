from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from blackbricks.blackbricks import FormatConfig
from blackbricks.cli import process_files
from blackbricks.files import LocalFile


def test_check_test_notebook():

    f = StringIO()
    with redirect_stdout(f):

        process_files(
            [LocalFile(Path(__file__).parent.parent / "test_notebooks" / "test.py")],
            format_config=FormatConfig(),
            check=True,
        )
    assert f.getvalue() == "All done!\n1 files would be left unchanged\n"


def test_check_test_notebook_with_newline():
    """Test formatting notebooks that should end in newline."""

    f = StringIO()
    with redirect_stdout(f):
        process_files(
            [LocalFile(Path(__file__).parent.parent / "test_notebooks" / "test_end_newline.py")],
            format_config=FormatConfig(end_in_newline=True),
            check=True,
        )
    assert f.getvalue() == "All done!\n1 files would be left unchanged\n"
