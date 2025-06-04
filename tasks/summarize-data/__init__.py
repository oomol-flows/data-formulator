#region generated meta
import typing
from oocana import Context
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
    file_name = params["file_name"]
    rows = params["data_rows"]
    
    if len(rows) == 0:
        raise Exception("No data rows found")
    
    llm_client = Client(
        endpoint="openai",
        api_base=context.oomol_llm_env.get("base_url_v1"),
        model="oomol-chat",
        api_key=context.oomol_llm_env.get("api_key")
    )
    
    # 读取部分数据，让ai 给出数据的schema和数据的描述
    agent = DataLoadAgent(client=llm_client, logger=context.logger)
    candidates = agent.run(input_data={
        "name": file_name,
        "rows": rows
    })
    candidates = [c['content'] for c in candidates if c['status'] == 'ok']
    
    context.preview(TextPreviewPayload(
        type= "text",
        data= candidates[0]["data summary"]
    ))
    return { "summary": candidates[0]["data summary"], "fields_schema": candidates[0]["fields"] }
