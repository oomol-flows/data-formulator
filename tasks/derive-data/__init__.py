#region generated meta
import typing
class Inputs(typing.TypedDict):
    file_name: str
    data_rows: list[typing.Any]
    instruction: str
    x_axis_name: str
    y_axis_name: str
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

    file_name = params["file_name"]
    rows = params["data_rows"]
    instruction = params["instruction"]

    x_axis_name = params["x_axis_name"]
    y_axis_name = params["y_axis_name"]
    
    if len(rows) == 0:
        raise Exception("No data rows found")
    
    llm_client = Client(
        endpoint="openai",
        api_base=context.oomol_llm_env.get("base_url_v1"),
        model="oomol-chat",
        api_key=context.oomol_llm_env.get("api_key")
    )

    input_tables = [{
        "name": file_name,
        "rows": rows
    }]
    new_fields = [{"name": x_axis_name}, {"name": y_axis_name}]

    print("== input tables ===>")
    for table in input_tables:
        print(f"===> Table: {table['name']} (first 5 rows)")
        print(table['rows'][:5])

    print("== user spec ===")
    print(new_fields)
    print(instruction)

    max_repair_attempts  =1
    agent = DataTransformationAgentV2(client=llm_client)
    results = agent.run(input_tables, instruction, [field['name'] for field in new_fields], [], max_repair_attempts)

    repair_attempts = 0
    while results[0]['status'] == 'error' and repair_attempts < max_repair_attempts: # try up to n times
        error_message = results[0]['content']
        new_instruction = f"We run into the following problem executing the code, please fix it:\n\n{error_message}\n\nPlease think step by step, reflect why the error happens and fix the code so that no more errors would occur."

        prev_dialog = results[0]['dialog']

        # 加上上一次的运行结果，加上修复 prompt 重新运行一次
        results = agent.followup(input_tables, prev_dialog, [field['name'] for field in new_fields], new_instruction)

        repair_attempts += 1

    res = results[0]
    if res is not None:
        code = res['code']
        content = res['content']
        refined_x_axis_name = res['refined_goal']['visualization_fields'][0]
        refined_y_axis_name = res['refined_goal']['visualization_fields'][1]
    else:
        raise Exception("No results found")

    code_expl_agent = CodeExplanationAgent(client=llm_client)
    expl = code_expl_agent.run(input_tables, code)

    return { "code_for_derive": code, "code_explain": expl, "content": content, "refined_x_axis_name": refined_x_axis_name, "refined_y_axis_name": refined_y_axis_name } 