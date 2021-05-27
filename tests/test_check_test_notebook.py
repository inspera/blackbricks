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
            format_config=FormatConfig(two_space_indent=True),
            check=True,
        )
    assert f.getvalue() == "All done!\n1 files would be left unchanged\n"
