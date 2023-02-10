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
        """
        Get the content of the notebook as a string.

        Note: Databricks will not include a trailing newlines from a notebook.
        That is, even if you checkout a notebook from a repo where there is a trailing
        newline, Databricks won't "show" an empty line in the UI. And similarly, this
        API doesn't include it. This contrasts with the prefered style of terminating
        the files with a newline, as enforced by black and blackbricks. To avoid
        perpetually reporting diffs due to newlines, we add a trailing newline to the
        content, _assuming_ that the
        we assume it to be present and add it back if it is missing. Failing to do this
        will cause blackbricks to perpetually report that it wants to add a trailing
        newline to remote notebooks.
        """
        return self.api_client.read_notebook(self.path) + "\n"

    @content.setter
    def content(self, new_content: str, /) -> None:
        """
        Set the content of the notebook to the given string.

        Note: We do _not_ need to do the inverse handling of trailing newlines as in
        the getter. The new content here is presumably the output of blackbricks, and
        we should let Databricks import that from the same source as it would find by
        checking out a repo notebook that has been formatted with blackbricks.
        """
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
