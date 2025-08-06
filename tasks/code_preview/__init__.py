#region generated meta
import typing
class Inputs(typing.TypedDict):
    input: str
Outputs = typing.Dict[str, typing.Any]
#endregion

from oocana.preview import TextPreviewPayload
from oocana import Context

def main(params: Inputs, context: Context) -> Outputs:

    payload=dict(
        type= "text/python",
        data= params["input"]
    )
    # your code
    context.preview(payload) # type: ignore
