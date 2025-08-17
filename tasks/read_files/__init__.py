import json
import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd
from oocana import Context

#region generated meta
import typing
class Inputs(typing.TypedDict):
    input: list[str]
    enable_preview: bool
class Outputs(typing.TypedDict):
    output: list[dict]
#endregion

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.error(f"读取文件失败 {file_path}: {str(e)}")
        raise


def dataframe_to_json_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """将DataFrame转换为JSON记录格式"""
    try:
        json_str = df.to_json(orient="records", force_ascii=False)
        return json.loads(json_str) if json_str else []
    except Exception as e:
        logger.error(f"数据转换失败: {str(e)}")
        return []


def process_single_file(file_path: str, enable_preview: bool, context: Context) -> Dict[str, Any]:
    """处理单个文件"""
    try:
        logger.info(f"开始处理文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取文件
        df = read_file_to_dataframe(file_path)
        
        # 获取文件名
        file_name = os.path.basename(file_path)
        
        # 转换为JSON
        records = dataframe_to_json_records(df)
        
        # 预览数据
        if enable_preview and context:
            context.preview(df)
            
        logger.info(f"成功处理文件: {file_name}, 记录数: {len(records)}")
        
        return {"name": file_name, "rows": records}
    except Exception as e:
        logger.error(f"处理文件失败 {file_path}: {str(e)}")
        return {"name": os.path.basename(file_path), "rows": [], "error": str(e)}


def main(params: Inputs, context: Context) -> Outputs:
    """主函数：处理多个文件"""
    try:
        input_files: List[str] = params.get("input", [])
        enable_preview: bool = params.get("enable_preview", False)
        
        if not input_files:
            logger.warning("没有提供输入文件")
            return {"output": []}
        
        logger.info(f"开始处理 {len(input_files)} 个文件")
        
        results = []
        for file_path in input_files:
            result = process_single_file(file_path, enable_preview, context)
            results.append(result)
        
        logger.info(f"完成处理，共处理 {len(results)} 个文件")
        return {"output": results}
        
    except Exception as e:
        logger.error(f"主程序执行失败: {str(e)}")
        return {"output": []}
