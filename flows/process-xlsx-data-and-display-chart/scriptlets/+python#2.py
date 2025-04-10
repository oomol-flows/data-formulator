import json
from oocana import Context
import pandas as pd
import os

def main(params: dict, context: Context):
    xlsx_file = params.get("input")
    assert xlsx_file is not None
    df = pd.read_excel(xlsx_file)
    # 读取文件名
    file_name = os.path.basename(xlsx_file)
    try:
       j = df.to_json(orient="records",force_ascii=False)
    except Exception as e:
        print(e)
    if j is not None:
        jd = json.loads(j)
    
    return {"file_name": file_name, "output": jd}
