#region generated meta
import typing
from oocana import Context
class Inputs(typing.TypedDict):
    data: list[typing.Any]
    x_column: str
    y_column: str
Outputs = typing.Dict[str, typing.Any]
#endregion

from oocana import Context
import pandas as pd
import plotly.express as px

def main(params: dict, context: Context):
    title = "result"
    df = pd.DataFrame(params["data"])

    assert df is not None
    x_column = params.get("x_column")
    y_column = params.get("y_column")

    fig = px.bar(
        df,
        x=x_column,
        y=y_column,
        title=title,
        color=x_column,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    fig.show()


