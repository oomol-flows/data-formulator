#region generated meta
import typing
class Inputs(typing.TypedDict):
    input: str
Outputs = typing.Dict[str, typing.Any]
#endregion

from oocana.preview import TextPreviewPayload
from oocana import Context

def main(params: Inputs, context: Context) -> None:

    # your code
    context.preview(payload=TextPreviewPayload(
        type= "text",
        data= params["input"]
    ))
