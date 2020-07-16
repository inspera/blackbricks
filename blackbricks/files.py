import os
from dataclasses import dataclass
from typing import Sequence

import typer

from .databricks_sync import DatabricksAPI


@dataclass
class File:
    path: str

    @property
    def content(self):
        raise NotImplementedError(
            "Do not use this class directly, use one of its subclasses."
        )

    @content.setter
    def content(self, new_content):
        raise NotImplementedError(
            "Do not use this class directly, use one of its subclasses."
        )


class LocalFile(File):
    @property
    def content(self):
        with open(self.path) as f:
            return f.read()

    @content.setter
    def content(self, new_content):
        with open(self.path, "w") as f:
            f.write(new_content)


@dataclass
class RemoteNotebook(File):
    api_client: DatabricksAPI

    @property
    def content(self):
        return self.api_client.read_notebook(self.path)

    @content.setter
    def content(self, new_content):
        self.api_client.write_notebook(self.path, new_content)


def resolve_filepaths(paths: Sequence[str]):
    """Resolve the paths given into valid file names

    Directories are recursively added, similarly to how black operates.

    :param paths: Sequence of paths to files or directories.
    :return: Absolute paths to all files given, including all files in any
             directories given, including subdirectories.
    """
    paths = list(paths)
    file_paths = []
    while paths:
        path = os.path.abspath(paths.pop())

        if not os.path.exists(path):
            typer.echo(
                typer.style("Error:", fg=typer.colors.RED)
                + " No such file or directory: "
                + typer.style(path, fg=typer.colors.CYAN)
            )
            raise typer.Exit(1)

        if os.path.isdir(path):

            # Recursively  add all the files/dirs in path to the paths to be consumed.
            paths.extend([os.path.join(path, f) for f in os.listdir(path)])

        else:

            file_paths.append(path)

    return file_paths
