import base64
import re
import os

import typer
from databricks_cli.sdk.api_client import ApiClient
from databricks_cli.sdk.service import WorkspaceService


class DatabricksAPI:
    def __init__(
        self, databricks_host: str, databricks_token: str, username: str = None
    ) -> WorkspaceService:
        self.client = WorkspaceService(
            ApiClient(host=databricks_host, token=databricks_token)
        )
        self.username = username

    def __resolve_path(self, path) -> str:
        """
        Resolve path to notebook.

        If `path` is not absolute and a username is in use, interpret the path as
        relative to the user direcotry.

        Example:

            tmp/notebook.py  -> /Users/{username}/tmp/notebook.py
            /tmp/notebook.py -> /tmp/notebook.py
        """
        if not path.startswith("/") and self.username is not None:
            path = f"/Users/{self.username}/{path}"
        return path

    def read_notebook(self, path) -> str:
        path = self.__resolve_path(path)
        response = self.client.export_workspace(path, format="SOURCE")

        assert (
            response["file_type"] == "py"
        ), f"Cannot read a non-python notebook: {path}"

        return base64.decodebytes(response["content"].encode()).decode()

    def write_notebook(self, path: str, content: str) -> None:
        path = self.__resolve_path(path)
        self.client.import_workspace(
            path,
            format="SOURCE",
            language="PYTHON",
            content=base64.b64encode(content.encode()).decode(),
            overwrite=True,
        )


def get_api_client(profile_name: str):
    try:
        with open(os.path.expanduser("~/.databrickscfg")) as f:
            content = f.read()
            match = re.match(
                r"\[{0}\](?P<profile>.*?)((\s\[\w+\])|$)".format(profile_name),
                content,
                flags=re.DOTALL,
            )
            assert match is not None

    except (FileNotFoundError, AssertionError):
        typer.echo(
            typer.style("Error:", fg=typer.colors.RED, bold=True)
            + typer.style(
                f" Could not find {profile_name} in ~/.databrickscfg", bold=True
            ),
        )
        typer.echo(
            "Run `databricks configure` and/or check your ~/.databrickscfg file."
        )
        raise typer.Abort()

    profile_config = match.group("profile")

    host = re.match(r".*host = (\S+)", profile_config, flags=re.DOTALL).groups()[0]
    username = re.match(
        r".*username = (\S+)", profile_config, flags=re.DOTALL
    ).groups()[0]
    password = re.match(
        r".*password = (\S+)", profile_config, flags=re.DOTALL
    ).groups()[0]

    return DatabricksAPI(
        databricks_host=host, databricks_token=password, username=username
    )
