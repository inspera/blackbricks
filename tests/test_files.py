from pathlib import Path

import click.testing

import pytest
from blackbricks.files import resolve_filepaths, File, LocalFile, RemoteNotebook

def test_file():
    """Test the File dataclass."""
    expected = File(path='test123')

    result = File("test123")

    assert result == expected

def test_file_should_not_use_content():
    """Test the File dataclass should not allow content."""
    file = File("test456")

    with pytest.raises(NotImplementedError) as pytest_wrapped_e:
        file.content

    assert pytest_wrapped_e.type == NotImplementedError


def test_file_should_not_set():
    """Test the File dataclass should not allow content."""
    file = File("test456")

    with pytest.raises(NotImplementedError) as pytest_wrapped_e:
        file.content = "test789"

    assert pytest_wrapped_e.type == NotImplementedError


def test_localfile():
    """Test the LocalFile dataclass."""
    expected = LocalFile(path='test123')

    result = LocalFile("test123")

    assert result == expected


def test_resolve_filepaths():
    """Test that the resolve_filepaths function works as expected."""
    file_paths = resolve_filepaths(["tests\\test_files.py"])

    result = Path(file_paths[0]).is_file()

    assert result is True


def test_no_unresolved_filepaths():
    """Test that typer exits with no such file or directory error."""
    with pytest.raises(click.exceptions.Exit) as pytest_wrapped_e:
        resolve_filepaths(["tests\\test123"])

    assert pytest_wrapped_e.type == click.exceptions.Exit


def test_resolve_filepaths_adds_dir():
    """Test that the resolve_filepaths adds a directory."""
    file_paths = resolve_filepaths(["tests\\"])

    result = Path(file_paths[0]).is_file()

    assert result is True
