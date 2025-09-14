#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[typing.Any]
    title: str | None
    x_column: str | None
    y_column: str | None
    chart_type: typing.Literal["bar", "line", "scatter", "pie", "histogram", "box", "area", "radar", "heatmap", "violin", "bubble"]
class Outputs(typing.TypedDict):
    status: str
    chart_type: str
    columns_used: list[typing.Any]
    data_points: float
#endregion

from oocana import Context
import pandas as pd
import plotly.express as px
import numpy as np
from typing import Optional, List

def _get_column_name(
    requested_col: Optional[str], 
    available_cols: List[str], 
    position: int, 
    special_cases: dict
) -> str:
    """获取有效的列名，处理特殊情况和默认值"""
    if not available_cols:
        raise ValueError("数据中没有可用列")
    
    # 处理特殊请求
    if requested_col and requested_col in special_cases:
        return requested_col
    
    # 如果请求的列存在，直接使用
    if requested_col and requested_col in available_cols:
        return requested_col
    
    # 根据位置选择默认列
    if position < len(available_cols):
        default_col = available_cols[position]
        # 使用默认列
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
    
    valid_chart_types = ['bar', 'line', 'scatter', 'pie', 'histogram', 'box', 'area', 'radar', 'heatmap', 'violin', 'bubble']
    if requested_type and requested_type in valid_chart_types:
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
    elif chart_type == 'area':
        fig = px.area(
            df, x=x_col, y=y_col, title=title,
            line_shape='linear', markers=True
        )
    elif chart_type == 'violin':
        if y_col and pd.api.types.is_numeric_dtype(df[y_col]):
            fig = px.violin(df, x=x_col, y=y_col, title=title, box=True)
        else:
            fig = px.violin(df, y=x_col, title=title, box=True)
    elif chart_type == 'bubble':
        # 气泡图需要至少3个数值列，使用第三列作为气泡大小
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 3 and y_col in numeric_cols:
            size_col = [col for col in numeric_cols if col not in [x_col, y_col]][0]
            fig = px.scatter(
                df, x=x_col, y=y_col, size=size_col, title=title,
                hover_data=df.columns.tolist(),
                color=x_col if len(df[x_col].unique()) < 10 else None
            )
        else:
            # 如果不足3个数值列，退化为普通散点图
            fig = px.scatter(df, x=x_col, y=y_col, title=title)
    elif chart_type == 'heatmap':
        # 热力图需要数值数据
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] >= 2:
            # 计算相关性矩阵
            corr_matrix = numeric_df.corr()
            fig = px.imshow(
                corr_matrix, 
                title=title or "相关性热力图",
                labels=dict(color="相关性"),
                color_continuous_scale="RdBu_r",
                aspect="auto"
            )
        else:
            # 如果数据不足，创建二维热力图
            fig = px.density_heatmap(
                df, x=x_col, y=y_col, title=title,
                marginal_x="histogram", marginal_y="histogram"
            )
    elif chart_type == 'radar':
        # 雷达图需要数值数据，且适合多维度对比
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 3:
            # 使用平均值创建雷达图
            avg_values = df[numeric_cols].mean()
            fig = px.line_polar(
                r=avg_values.values, theta=avg_values.index,
                line_close=True, title=title
            )
            fig.update_traces(fill='toself')
        else:
            # 如果数据不足，创建简单的雷达图
            fig = px.line_polar(
                df, r=y_col, theta=x_col, line_close=True, title=title
            )
            fig.update_traces(fill='toself')
    else:
        # 默认柱状图
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    
    return fig

def main(params: Inputs, context: Context) -> Outputs:
    """根据分析需求动态创建图表"""
    
    # 使用 context 参数避免未使用警告
    _ = context
    try:
        # 验证输入参数
        if not params:
            raise ValueError("输入参数为空")
        
        # 检查 data 字段
        data_input = params.get("data")
        
        if data_input is None:
            raise ValueError("数据为空，可能是上游任务未正确输出数据")
        
        if not isinstance(data_input, list):
            raise ValueError(f"数据格式错误，应为列表类型，实际为: {type(data_input)}")
        
        if len(data_input) == 0:
            raise ValueError("数据为空，没有可处理的内容")
        
        # 参数准备
        title = params.get("title") or "分析结果"
        
        try:
            df = pd.DataFrame(data_input)
        except Exception as e:
            raise ValueError(f"数据转换失败: {str(e)}")
        
        if df.empty:
            raise ValueError("转换后的数据为空")
        
        available_columns = df.columns.tolist()
        if not available_columns:
            raise ValueError("数据中没有可用列")
        
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
        
        # 生成图表
        
        # 准备数据
        df, final_x_col, final_y_col = _prepare_dataframe(df, x_column, y_column)
        
        # 创建图表
        try:
            fig = _create_chart(df, chart_type, final_x_col, final_y_col, title)
            fig.show()
        except Exception as e:
            raise RuntimeError(f"图表创建失败: {str(e)}")
        
        return {
            "status": "success", 
            "chart_type": chart_type,
            "columns_used": [final_x_col, final_y_col],
            "data_points": len(df)
        }
        
    except Exception as e:
        raise