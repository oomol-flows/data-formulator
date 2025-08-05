from typing import Any

import json
from oocana import Context
import pandas as pd
import os

#region generated meta
import typing
class Inputs(typing.TypedDict):
    input: list[str]
    enable_preview: bool
class Outputs(typing.TypedDict):
    output: list[dict]
#endregion


def main(params: Inputs, context: Context) -> Outputs:
    input_files: Any | None = params.get("input")
    enable_preview: bool = params.get("enable_preview", False)
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
            jd = json.loads(j) if j is not None else []
        except Exception as e:
            print(e)
            jd = []
        output.append({"name": file_name, "rows": jd})
        
        # 根据 enable_preview 参数决定是否执行预览
        if enable_preview:
            context.preview(df)
    return {"output": output}
