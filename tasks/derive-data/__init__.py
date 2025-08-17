#region generated meta
import typing
from oocana import LLMModelOptions
class Inputs(typing.TypedDict):
    data: list[dict]
    instruction: str
    x_axis_name: str | None
    y_axis_name: str | None
    code_repair_attempts: int | None
    llm_model: LLMModelOptions
class Outputs(typing.TypedDict):
    code_for_derive: str
    code_explain: str
    content: list[typing.Any]
    refined_x_axis_name: str
    refined_y_axis_name: str
#endregion

from data_formulator.agents.agent_code_explanation import CodeExplanationAgent
from data_formulator.agents.agent_data_transform_v2 import DataTransformationAgentV2
from data_formulator.agents.client_utils import Client
from oocana import Context

def _validate_inputs(params: Inputs) -> None:
    """验证输入参数"""
    if not params.get("data"):
        raise ValueError("未提供数据")
    if not params.get("instruction"):
        raise ValueError("未提供指令")
    if not isinstance(params["data"], list):
        raise ValueError("数据格式错误，应为列表类型")

def _create_llm_client(params: Inputs, context: Context) -> Client:
    """创建 LLM 客户端"""
    llm_model = params.get("llm_model", {})
    return Client(
        endpoint="openai",
        api_base=context.oomol_llm_env.get("base_url_v1"),
        model=llm_model.get("model", "oomol-chat"),
        api_key=context.oomol_llm_env.get("api_key")
    )

def _process_data_with_repair(agent, input_tables: list, instruction: str, 
                             expected_fields: list, max_attempts: int) -> dict:
    """处理数据转换并自动修复错误"""
    try:
        results = agent.run(input_tables, instruction, expected_fields, [], max_attempts)
        
        repair_attempts = 0
        while results[0]['status'] == 'error' and repair_attempts < max_attempts:
            # 代码错误，尝试修复
            error_message = results[0]['content']
            repair_instruction = (
                f"遇到以下错误：\n\n{error_message}\n\n"
                "请分析错误并修复代码以防止类似问题。"
            )
            
            prev_dialog = results[0]['dialog']
            results = agent.followup(input_tables, prev_dialog, expected_fields, repair_instruction)
            repair_attempts += 1
        
        if results[0]['status'] == 'error':
            raise RuntimeError(f"经过 {max_attempts} 次尝试后仍无法生成有效代码")
        
        return results[0]
    except Exception as e:
        raise RuntimeError(f"数据处理失败: {str(e)}")

def _determine_axis_names(result: dict, x_axis_name: str | None, y_axis_name: str | None) -> tuple[str, str]:
    """确定轴名称"""
    visualization_fields = result.get('refined_goal', {}).get('visualization_fields', [])
    content = result.get('content', [])
    
    # 获取数据中可用的列
    available_columns = []
    if content and isinstance(content[0], dict):
        available_columns = list(content[0].keys())
    
    # 确定 x 轴名称
    if x_axis_name:
        refined_x = x_axis_name
    elif visualization_fields:
        refined_x = visualization_fields[0]
    elif available_columns:
        refined_x = available_columns[0]
    else:
        refined_x = "index"
    
    # 确定 y 轴名称
    if y_axis_name:
        refined_y = y_axis_name
    elif len(visualization_fields) >= 2:
        refined_y = visualization_fields[1]
    else:
        refined_y = "count"
    
    return refined_x, refined_y

def main(params: Inputs, context: Context) -> Outputs:
    # 验证输入参数
    _validate_inputs(params)
    
    # 提取参数
    input_tables = params["data"]
    instruction = params["instruction"]
    max_repair_attempts = params.get("code_repair_attempts", 3)
    x_axis_name = params.get("x_axis_name")
    y_axis_name = params.get("y_axis_name")
    
    # 创建 LLM 客户端
    llm_client = _create_llm_client(params, context)
    
    # 构建预期字段列表
    expected_fields = [name for name in [x_axis_name, y_axis_name] if name is not None]
    
    # 处理输入数据
    
    # 创建数据转换代理并处理
    agent = DataTransformationAgentV2(client=llm_client)
    result = _process_data_with_repair(agent, input_tables, instruction, expected_fields, max_repair_attempts)
    
    # 提取结果
    code = result['code']
    content = result['content']
    
    # 确定轴名称
    refined_x_axis_name, refined_y_axis_name = _determine_axis_names(result, x_axis_name, y_axis_name)
    
    # 生成代码解释
    code_expl_agent = CodeExplanationAgent(client=llm_client)
    code_explain = code_expl_agent.run(input_tables, code)
    
    return {
        "code_for_derive": code,
        "code_explain": code_explain,
        "content": content,
        "refined_x_axis_name": refined_x_axis_name,
        "refined_y_axis_name": refined_y_axis_name
    } 