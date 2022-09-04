from enum import Enum
from typing import Literal, TypedDict

from _typeshed import Incomplete

from .api_client import ApiClient

class ObjectType(Enum):
    directory = "DIRECTORY"
    notebook = "NOTEBOOK"
    library = "LIBRARY"
    repo = "REPO"

class ListEntry(TypedDict):
    path: str
    object_type: ObjectType

class ListReponse(TypedDict):
    objects: list[ListEntry]

class ExportResponse(TypedDict):
    content: str

class WorkspaceService:
    client: Incomplete
    def __init__(self, client: ApiClient) -> None: ...
    def list(self, path: str) -> ListReponse: ...
    def import_workspace(
        self,
        path: str,
        *,
        format: Literal["SOURCE"],
        language: Literal["PYTHON"],
        content: str,
        overwrite: bool
    ) -> None: ...
    def export_workspace(
        self, path: str, *, format: Literal["SOURCE"]
    ) -> ExportResponse: ...
