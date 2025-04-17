from typing import Any

import json
from oocana import Context
import pandas as pd
import os

def main(params: dict, context: Context):
    input_files: Any | None = params.get("input")
    assert input_files is not None
    assert len(input_files) > 0 

    output = []
    for file in input_files:
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext == ".xlsx":
            df = pd.read_excel(file)
        elif file_ext == ".csv":
            df = pd.read_csv(file)
        else:
            raise ValueError("Unsupported file format. Only .xlsx and .csv are supported.")

        # 读取文件名
        file_name = os.path.basename(file)
        try:
            j = df.to_json(orient="records",force_ascii=False)
        except Exception as e:
            print(e)
        if j is not None:
            jd = json.loads(j)
        output.append({"name": file_name, "rows": jd})
        context.preview(df)
    return {"output": output}
