#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[typing.Any]
    title: str | None
    x_column: str | None
    y_column: str | None
    chart_type: typing.Literal["bar", "line", "scatter", "pie", "histogram", "box"]
class Outputs(typing.TypedDict):
    status: str
    chart_type: str
    columns_used: list[typing.Any]
    data_points: float
#endregion

from oocana import Context
import pandas as pd
import plotly.express as px
from typing import Optional, List

def _get_column_name(
    requested_col: Optional[str], 
    available_cols: List[str], 
    position: int, 
    special_cases: dict
) -> str:
    """获取有效的列名，处理特殊情况和默认值"""
    
    # 处理特殊请求
    if requested_col and requested_col in special_cases:
        return requested_col
    
    # 如果请求的列存在，直接使用
    if requested_col and requested_col in available_cols:
        return requested_col
    
    # 根据位置选择默认列
    if position < len(available_cols):
        default_col = available_cols[position]
        if requested_col:
            print(f"列 '{requested_col}' 不存在，使用 '{default_col}' 替代")
        else:
            print(f"使用第 {position + 1} 列 '{default_col}' 作为默认值")
        return default_col
    
    raise ValueError(f"数据中没有足够的列，至少需要 {position + 1} 列")

def _prepare_dataframe(df: pd.DataFrame, x_col: str, y_col: str) -> tuple[pd.DataFrame, str, str]:
    """准备数据框，处理特殊列需求"""
    
    # 处理索引列
    if x_col == "index":
        df = df.reset_index()
        return df, "index", y_col
    
    # 处理计数列
    if y_col == "count":
        df = df.copy()
        df['count'] = 1
        return df, x_col, "count"
    
    return df, x_col, y_col

def _determine_chart_type(df: pd.DataFrame, x_col: str, y_col: str, requested_type: Optional[str]) -> str:
    """根据数据特征和分析需求确定图表类型"""
    
    if requested_type and requested_type in ['bar', 'line', 'scatter', 'pie', 'histogram', 'box']:
        return requested_type
    
    # 自动分析数据特征
    x_dtype = df[x_col].dtype
    y_dtype = df[y_col].dtype if y_col in df.columns else None
    
    # 分类数据 + 数值数据 -> 柱状图
    if pd.api.types.is_object_dtype(x_dtype) or pd.api.types.is_categorical_dtype(x_dtype):
        if y_dtype and pd.api.types.is_numeric_dtype(y_dtype):
            return 'bar'
    
    # 时间序列数据 -> 折线图
    if pd.api.types.is_datetime64_any_dtype(x_dtype):
        return 'line'
    
    # 两个数值变量 -> 散点图
    if y_dtype and pd.api.types.is_numeric_dtype(x_dtype) and pd.api.types.is_numeric_dtype(y_dtype):
        return 'scatter'
    
    # 单一数值列 -> 直方图
    if y_dtype and pd.api.types.is_numeric_dtype(y_dtype):
        return 'histogram'
    
    # 默认使用柱状图
    return 'bar'

def _create_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, title: str):
    """根据类型创建图表"""
    
    if chart_type == 'bar':
        fig = px.bar(
            df, x=x_col, y=y_col, title=title,
            color=x_col, color_discrete_sequence=px.colors.qualitative.Plotly
        )
    elif chart_type == 'line':
        fig = px.line(
            df, x=x_col, y=y_col, title=title,
            markers=True, line_shape='linear'
        )
    elif chart_type == 'scatter':
        fig = px.scatter(
            df, x=x_col, y=y_col, title=title,
            color=x_col if len(df[x_col].unique()) < 10 else None,
            trendline="ols" if pd.api.types.is_numeric_dtype(df[x_col]) else None
        )
    elif chart_type == 'pie':
        if y_col:
            fig = px.pie(df, names=x_col, values=y_col, title=title)
        else:
            value_counts = df[x_col].value_counts().reset_index()
            value_counts.columns = [x_col, 'count']
            fig = px.pie(value_counts, names=x_col, values='count', title=title)
    elif chart_type == 'histogram':
        if y_col and pd.api.types.is_numeric_dtype(df[y_col]):
            fig = px.histogram(df, x=y_col, title=title, nbins=min(50, len(df)//5))
        else:
            fig = px.histogram(df, x=x_col, title=title, nbins=min(50, len(df)//5))
    elif chart_type == 'box':
        if y_col and pd.api.types.is_numeric_dtype(df[y_col]):
            fig = px.box(df, x=x_col, y=y_col, title=title)
        else:
            fig = px.box(df, y=x_col, title=title)
    else:
        # 默认柱状图
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    
    return fig

def main(params: Inputs, context: Context) -> Outputs:
    """根据分析需求动态创建图表"""
    
    # 使用 context 参数避免未使用警告
    _ = context
    try:
        # 调试输入参数
        print("== result_chart 输入参数调试 ===")
        print(f"输入参数类型: {type(params)}")
        print(f"输入参数内容: {params}")
        
        # 检查 data 字段
        data_input = params.get("data")
        print(f"data 字段类型: {type(data_input)}")
        print(f"data 字段内容: {data_input}")
        
        if data_input is None:
            raise ValueError("data 字段为 None，可能是上游任务未正确输出数据")
        
        if not isinstance(data_input, list):
            raise ValueError(f"data 字段应为列表类型，实际为: {type(data_input)}")
        
        if len(data_input) == 0:
            raise ValueError("data 字段为空列表，没有可处理的数据")
        
        # 参数准备
        title = params.get("title") or "分析结果"
        df = pd.DataFrame(data_input)
        
        if df.empty:
            raise ValueError("转换为 DataFrame 后数据为空")
        
        available_columns = df.columns.tolist()
        print(f"可用列: {available_columns}")
        
        # 获取有效的列名
        x_column = _get_column_name(
            params.get("x_column"),
            available_columns,
            0,  # 第一列作为x轴默认值
            {"index": "index"}
        )
        
        y_column = _get_column_name(
            params.get("y_column"),
            available_columns,
            1 if len(available_columns) > 1 else 0,  # 第二列或第一列作为y轴默认值
            {"count": "count"}
        )
        
        # 确定图表类型
        chart_type = _determine_chart_type(
            df, x_column, y_column, params.get("chart_type")
        )
        
        print(f"图表类型: {chart_type}, x_column: {x_column}, y_column: {y_column}")
        
        # 准备数据
        df, final_x_col, final_y_col = _prepare_dataframe(df, x_column, y_column)
        
        # 创建图表
        fig = _create_chart(df, chart_type, final_x_col, final_y_col, title)
        
        fig.show()
        
        return {
            "status": "success", 
            "chart_type": chart_type,
            "columns_used": [final_x_col, final_y_col],
            "data_points": len(df)
        }
        
    except Exception as e:
        print(f"创建图表时出错: {str(e)}")
        raise