#region generated meta
import typing
class Inputs(typing.TypedDict):
    file_name: str
    data_rows: list[typing.Any]
class Outputs(typing.TypedDict):
    summary: str
    fields_schema: list[typing.Any]
#endregion

from oocana.preview import TextPreviewPayload
from data_formulator.agents.agent_data_load import DataLoadAgent
from data_formulator.agents.client_utils import Client
from oocana import Context

def main(params: Inputs, context: Context) -> Outputs:
    """数据摘要生成功能"""
    try:
        # 验证输入参数
        if not params:
            raise ValueError("输入参数为空")
        
        file_name = params.get("file_name")
        rows = params.get("data_rows", [])
        
        if not file_name:
            raise ValueError("未提供文件名")
        
        if not rows or len(rows) == 0:
            raise ValueError("没有找到数据行")
        
        # 创建 LLM 客户端
        try:
            llm_client = Client(
                endpoint="openai",
                api_base=context.oomol_llm_env.get("base_url_v1"),
                model="oomol-chat",
                api_key=context.oomol_llm_env.get("api_key")
            )
        except Exception as e:
            raise RuntimeError(f"LLM 客户端创建失败: {str(e)}")
        
        # 使用 AI 分析数据
        agent = DataLoadAgent(client=llm_client, logger=context.logger)
        candidates = agent.run(input_data={
            "name": file_name,
            "rows": rows
        })
        
        # 过滤成功的结果
        valid_candidates = [c['content'] for c in candidates if c['status'] == 'ok']
        
        if not valid_candidates:
            raise RuntimeError("数据分析失败，未获得有效结果")
        
        result = valid_candidates[0]
        summary = result.get("data summary", "无法生成数据摘要")
        fields_schema = result.get("fields", [])
        
        # 预览结果
        try:
            context.preview(TextPreviewPayload(
                type="markdown",
                data=summary
            ))
        except Exception as preview_error:
            context.logger.warning(f"预览失败: {str(preview_error)}")
        
        return {
            "summary": summary,
            "fields_schema": fields_schema
        }
        
    except Exception as e:
        error_msg = f"数据摘要生成失败: {str(e)}"
        context.logger.error(error_msg)
        
        # 预览错误信息
        try:
            context.preview(TextPreviewPayload(
                type="markdown",
                data=f"**错误**: {error_msg}"
            ))
        except:
            pass
        
        return {
            "summary": error_msg,
            "fields_schema": []
        }
