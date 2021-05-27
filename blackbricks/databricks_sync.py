import base64
import os
from configparser import ConfigParser

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
    config = ConfigParser()
    config_path = os.path.expanduser("~/.databrickscfg")
    try:
        config.read(config_path)
    except FileNotFoundError:
        typer.echo(
            typer.style("Error:", fg=typer.colors.RED, bold=True)
            + typer.style(
                " Your ~/.databrickscfg file is missing.",
                bold=True,
            ),
        )
        typer.echo(
            "If you haven't already, first install the databricks cli,\n"
            "then run `databricks configure` and check your ~/.databrickscfg file."
        )
        raise typer.Abort()
    except Exception as e:
        typer.echo(
            typer.style("Error:", fg=typer.colors.RED, bold=True)
            + typer.style(
                " An error occurred while reading your ~/.databrickscfg file.",
                bold=True,
            )
        )
        raise e

    if profile_name != "DEFAULT" and not config.has_section(profile_name):
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

    host = config.get(profile_name, "host")  # Will throw if missing, always needed.
    username = config.get(profile_name, "username", fallback=None)
    token = config.get(profile_name, "token", fallback=None)
    password = config.get(profile_name, "password", fallback=None)
    credentials = token if token is not None else password

    # Handle no username:
    if username is None:
        typer.echo(
            typer.style("Warning:", fg=typer.colors.YELLOW, bold=True)
            + typer.style(" No username in ~/.databrickscfg.", bold=True)
        )
        typer.echo(
            "Please add `username = ...` to your profile (and/or the [DEFAULT] profile)"
            ", or be sure to always write full paths to notebooks."
        )

    # Handle no token and no password:
    if credentials is None:
        typer.echo(
            typer.style("Error:", fg=typer.colors.RED, bold=True)
            + typer.style(
                f" Found neither token nor password in ~/.databrickscfg for profile {profile_name}",
                bold=True,
            ),
        )
        raise typer.Abort()

    # Handle password without a username:
    if token is None and password is not None and username is None:
        typer.echo(
            typer.style("Error:", fg=typer.colors.RED, bold=True)
            + typer.style(
                f" Profile {profile_name} is missing a username in ~/.databrickscfg",
                bold=True,
            ),
        )
        raise typer.Abort()

    # Handle both token and password (one might be from DEFAULT):
    if token is not None and password is not None:
        if password != config.defaults().get("password"):
            credentials = password
        if token != config.defaults().get("token"):
            credentials = token

    return DatabricksAPI(
        databricks_host=host, databricks_token=credentials, username=username
    )
