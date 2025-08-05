#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[typing.Any]
    x_column: str | None
    y_column: str | None
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

    # 检查指定的列是否存在于数据框中
    available_columns = df.columns.tolist()
    print(f"Available columns: {available_columns}")
    print(f"Requested x_column: {x_column}, y_column: {y_column}")

    # 处理 x_column 为 None 或不存在的情况
    if x_column is None or x_column not in available_columns:
        if x_column == "index":
            # 如果请求的是 index，则重置索引并使用索引作为列
            df = df.reset_index()
            x_column = "index"
        elif available_columns:
            # 使用第一个可用列
            original_x = x_column
            x_column = available_columns[0]
            if original_x is not None:
                print(f"x_column '{original_x}' not found, using '{x_column}' instead")
            else:
                print(f"x_column is None, using '{x_column}' as default")
        else:
            raise ValueError("No columns available in the data")

    # 处理 y_column 为 None 或不存在的情况
    if y_column is None or y_column not in available_columns:
        if y_column == "count":
            # 为每行创建计数列
            df['count'] = 1
            y_column = "count"
        elif available_columns and len(available_columns) > 1:
            # 使用第二个可用列
            original_y = y_column
            y_column = available_columns[1] if len(available_columns) > 1 else available_columns[0]
            if original_y is not None:
                print(f"y_column '{original_y}' not found, using '{y_column}' instead")
            else:
                print(f"y_column is None, using '{y_column}' as default")
        else:
            # 如果只有一列，创建计数列
            df['count'] = 1
            y_column = "count"
            if y_column is None:
                print("y_column is None, using 'count' as default")
            else:
                print(f"y_column '{y_column}' not found, using 'count' instead")

    fig = px.bar(
        df,
        x=x_column,
        y=y_column,
        title=title,
        color=x_column,
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )

    fig.show()