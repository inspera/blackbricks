import os
from dataclasses import dataclass
from typing import List

import typer

from .databricks_sync import DatabricksAPI, ObjectType


@dataclass
class File:
    path: str

    @property
    def content(self) -> str:
        raise NotImplementedError(
            "Do not use this class directly, use one of its subclasses."
        )

    @content.setter
    def content(self, _: str, /) -> None:
        raise NotImplementedError(
            "Do not use this class directly, use one of its subclasses."
        )


class LocalFile(File):
    @property
    def content(self) -> str:
        with open(self.path) as f:
            return f.read()

    @content.setter
    def content(self, new_content: str, /) -> None:
        with open(self.path, "w") as f:
            f.write(new_content)


@dataclass
class RemoteNotebook(File):
    api_client: DatabricksAPI

    @property
    def content(self) -> str:
        return self.api_client.read_notebook(self.path)

    @content.setter
    def content(self, new_content: str, /) -> None:
        self.api_client.write_notebook(self.path, new_content)


def resolve_filepaths(paths: List[str]) -> List[str]:
    """Resolve the paths given into valid file names

    Directories are recursively added, similarly to how black operates.

    :param paths: List of paths to files or directories.
    :return: Absolute paths to all files given, including all files in any
             directories given, including subdirectories.
    """
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


def resolve_databricks_paths(
    paths: List[str], *, api_client: DatabricksAPI
) -> List[str]:
    """Resolve the remote paths given into valid file names

    Directories are recursively added, similarly to how black operates.

    :param paths: List of paths to remote files or directories.
    :api_client: Databricks API client to use.
    :return: Absolute paths to all files given, including all files in any
             directories given, including subdirectories.
    """
    paths = [api_client._resolve_path(path) for path in paths]
    file_paths = []
    while paths:
        path = paths.pop()
        response = api_client.list_workspace(path)
        for file_obj in response:
            if (obj_type := file_obj["object_type"]) == ObjectType.notebook.value:
                file_paths.append(file_obj["path"])
            elif obj_type in (ObjectType.directory.value, ObjectType.repo.value):
                paths.append(file_obj["path"])
    return file_paths
