from oocana import Context

#region generated meta
import typing
class Inputs(typing.TypedDict):
    table: str
class Outputs(typing.TypedDict):
    tables: list[str]
#endregion

def main(params: Inputs, context: Context) -> Outputs:
    table = params.get("table")
    # your code

    return {
       "tables": [table]
    }
