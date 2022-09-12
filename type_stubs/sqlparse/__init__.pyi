from typing import Literal, Union

def format(
    sql: str, *, reindent: bool, keyword_case: Union[Literal["upper"], Literal["lower"]]
) -> str: ...
