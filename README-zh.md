# data-formulator

该项目基于 [microsoft/data-formulator](https://github.com/microsoft/data-formulator) 软件修改而来。

该项目用于将用户上传的表格类数据进行分析后，按照用户意愿进行自定义格式化输出。
项目利用 AI 分析用户意图，并将用户意图转化为代码，最后执行代码生成用户所需的格式化数据并以图标形式展示。

## Flow
* process-xlsx-data-and-display-chart
接收一个xlsx 格式的文件，将其内容按照用户的要求进行格式化，并以图表的形式展示。

## Shared Block
* derive-data
用户可以自行指定输出表格的横纵轴名称，同时可以自定义要求。AI 会根据输入的数据判断如何达成要求，生成代码并自动执行，最终输出符合用户要求的图表数据结构。

* summarize-data
总结输入数据（数组格式），大致描述输入是记录的什么内容，同事自动判断输入数据的格式。