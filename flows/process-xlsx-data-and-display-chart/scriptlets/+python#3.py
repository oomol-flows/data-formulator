#region generated meta
import typing
from oocana import Context
class Inputs(typing.TypedDict):
    input: str
Outputs = typing.Dict[str, typing.Any]
#endregion

from oocana.preview import TextPreviewPayload
from oocana import Context

def main(params: Inputs, context: Context) -> None:

    payload=dict(
        type= "text/python",
        data= params["input"]
    )
    # your code
    context.preview(payload) # type: ignore
