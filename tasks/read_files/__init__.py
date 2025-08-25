import json
import os
from typing import Any, Dict, List

import pandas as pd
from oocana import Context

#region generated meta
import typing
class Inputs(typing.TypedDict):
    tables: list[str]
    enable_preview: bool
class Outputs(typing.TypedDict):
    output: list[dict]
#endregion

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}


def read_file_to_dataframe(file_path: str) -> pd.DataFrame:
    """读取文件到DataFrame"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"不支持的文件格式: {file_ext}。"
            f"支持的格式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
    
    try:
        if file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif file_ext == '.csv':
            return pd.read_csv(file_path)
    except Exception as e:
        raise


def dataframe_to_json_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """将DataFrame转换为JSON记录格式"""
    try:
        json_str = df.to_json(orient="records", force_ascii=False)
        return json.loads(json_str) if json_str else []
    except Exception as e:
        return []


def process_single_file(file_path: str, enable_preview: bool, context: Context) -> Dict[str, Any]:
    """处理单个文件"""
    file_name = os.path.basename(file_path)
    
    try:
        # 读取文件
        df = read_file_to_dataframe(file_path)
        
        # 转换为JSON
        records = dataframe_to_json_records(df)
        
        # 预览数据
        if enable_preview and context and not df.empty:
            try:
                context.preview(df)
            except Exception:
                pass
            
        return {"name": file_name, "rows": records}
    except Exception as e:
        return {"name": file_name, "rows": [], "error": str(e)}


def main(params: Inputs, context: Context) -> Outputs:
    """主函数：处理多个文件"""
    try:
        # 验证输入参数
        if not params:
            return {"output": []}
        
        input_files: List[str] = params.get("tables", [])
        enable_preview: bool = params.get("enable_preview", False)
        
        if not input_files:
            return {"output": []}
        
        # 过滤空字符串和无效路径
        valid_files = [f for f in input_files if f and f.strip()]
        if not valid_files:
            return {"output": []}
        
        results = []
        for file_path in valid_files:
            result = process_single_file(file_path, enable_preview, context)
            results.append(result)
        
        return {"output": results}
        
    except Exception:
        return {"output": []}
