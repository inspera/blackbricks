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


def _get_option_if_exists(raw_config, profile, option):
    if profile == "DEFAULT":
        # We must handle the 'DEFAULT' differently since it is not in the _sections property
        # of raw config.
        return (
            raw_config.get(profile, option)
            if raw_config.has_option(profile, option)
            else None
        )
    # Check if option is defined in the profile.
    elif option not in raw_config._sections.get(profile, {}).keys():
        return None
    return raw_config.get(profile, option)


def get_api_client(profile_name: str):
    try:
        config_path = os.path.expanduser("~/.databrickscfg")
        raw_config = ConfigParser()
        raw_config.read(config_path)
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

    host = _get_option_if_exists(raw_config, profile_name, "host")
    username = _get_option_if_exists(raw_config, profile_name, "username")
    password = _get_option_if_exists(raw_config, profile_name, "password")
    token = _get_option_if_exists(raw_config, profile_name, "token")

    if (username != None) and (password != None):
        return DatabricksAPI(
            databricks_host=host, databricks_token=password, username=username
        )
    elif token != None:
        return DatabricksAPI(databricks_host=host, databricks_token=token)
    else:
        typer.echo(
            typer.style("Error:", fg=typer.colors.RED, bold=True)
            + typer.style(
                f" Found neither username + password nor token in ~/.databrickscfg",
                bold=True,
            ),
        )
        typer.echo(
            "Run `databricks configure` and/or check your ~/.databrickscfg file."
        )
        raise typer.Abort()
