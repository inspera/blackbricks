import base64

from databricks_cli.sdk.api_client import ApiClient
from databricks_cli.sdk.service import WorkspaceService


class DatabricksAPI:
    def __init__(self, databricks_host: str, databricks_token: str) -> WorkspaceService:
        self.client = WorkspaceService(
            ApiClient(host=databricks_host, token=databricks_token)
        )

    def read_notebook(self, path) -> str:
        response = self.client.export_workspace(path, format="SOURCE")

        assert (
            response["file_type"] == "py"
        ), f"Cannot read a non-python notebook: {path}"

        return base64.decodebytes(response["content"].encode()).decode()

    def write_notebook(self, path: str, content: str) -> None:
        self.client.import_workspace(
            path,
            format="SOURCE",
            language="PYTHON",
            content=base64.b64encode(content.encode()).decode(),
            overwrite=True,
        )
