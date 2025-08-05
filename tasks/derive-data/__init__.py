#region generated meta
import typing
class Inputs(typing.TypedDict):
    data: list[dict]
    code_repair_attempts: int | None
    x_axis_name: str | None
    y_axis_name: str | None
    instruction: str
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

def main(params: Inputs, context: Context) -> Outputs:
    input_tables = params["data"]
    instruction = params["instruction"]

    # 处理可选参数，设置默认值
    max_repair_attempts = params["code_repair_attempts"] or 3
    x_axis_name = params["x_axis_name"]
    y_axis_name = params["y_axis_name"]
    
    if len(input_tables) == 0:
        raise Exception("No data rows found")
    
    llm_client: Client = Client(
        endpoint="openai",
        api_base=context.oomol_llm_env.get("base_url_v1"),
        model="oomol-chat",
        api_key=context.oomol_llm_env.get("api_key")
    )

    # 构建预期字段列表，过滤掉 None 值
    expected_fields = [name for name in [x_axis_name, y_axis_name] if name is not None]

    print("== input tables ===>")
    for table in input_tables:
        print(f"===> Table: {table['name']} (first 5 rows)")
        print(table['rows'][:5])

    print("== user spec ===")
    print(f"Expected fields: {expected_fields}")
    print(instruction)

    agent = DataTransformationAgentV2(client=llm_client)
    results = agent.run(input_tables, instruction, expected_fields, [], max_repair_attempts)

    repair_attempts = 0
    while results[0]['status'] == 'error' and repair_attempts < max_repair_attempts: # try up to n times
        print("== code wrong, try repaire ===")
        error_message = results[0]['content']
        new_instruction = f"We run into the following problem executing the code, please fix it:\n\n{error_message}\n\nPlease think step by step, reflect why the error happens and fix the code so that no more errors would occur."

        prev_dialog = results[0]['dialog']

        # 加上上一次的运行结果，加上修复 prompt 重新运行一次
        results = agent.followup(input_tables, prev_dialog, expected_fields, new_instruction)
        repair_attempts += 1

    res = results[0]
    if res is not None:
        code = res['code']
        content = res['content']
        
        # 处理可选的轴名称，从 refined_goal 中获取实际的可视化字段
        visualization_fields = res['refined_goal']['visualization_fields']
        
        # 根据原始输入和 AI 推荐的字段确定最终的轴名称
        if len(visualization_fields) >= 2:
            refined_x_axis_name = visualization_fields[0]
            refined_y_axis_name = visualization_fields[1]
        elif len(visualization_fields) == 1:
            # 如果只有一个字段，根据原始输入决定它是 x 轴还是 y 轴
            if x_axis_name is not None:
                refined_x_axis_name = visualization_fields[0]
                refined_y_axis_name = y_axis_name or "count"  # 提供默认的 y 轴
            else:
                refined_x_axis_name = x_axis_name or visualization_fields[0]  # 使用可视化字段而不是 index
                refined_y_axis_name = "count"  # 提供默认的 y 轴用于计数
        else:
            # 如果没有可视化字段，检查数据中实际存在的列
            if content and len(content) > 0:
                # 获取数据中的第一个可用列作为 x 轴
                available_columns = list(content[0].keys()) if isinstance(content[0], dict) else []
                refined_x_axis_name = x_axis_name or (available_columns[0] if available_columns else "index")
                refined_y_axis_name = y_axis_name or "count"
            else:
                refined_x_axis_name = x_axis_name or "index"
                refined_y_axis_name = y_axis_name or "count"
    else:
        raise Exception("No results found")

    code_expl_agent = CodeExplanationAgent(client=llm_client)
    expl = code_expl_agent.run(input_tables, code)

    return { "code_for_derive": code, "code_explain": expl, "content": content, "refined_x_axis_name": refined_x_axis_name, "refined_y_axis_name": refined_y_axis_name } 