# data-formulator

This project is based on the [microsoft/data-formulator](https://github.com/microsoft/data-formulator) software.

This project is used to analyze user-uploaded tabular data and then output it in a custom format according to user requirements.
The project uses AI to analyze user intent, convert it into code, and finally execute the code to generate the required formatted data and display it in a chart.

The input file format should be a two-dimensional table. If the header is complex, the results may be inaccurate. Please organize the header yourself.

Due to the use of AI models to generate results, the results may not be consistent each time. If the results are inaccurate, please regenerate.

## Flow
### process-xlsx-data-and-display-chart

Receives an xlsx format file, formats its content according to user requirements, and displays it in a chart. The flow has the following inputs:
![flow](./flow.png)

1. input: Input file address array, you can add and select multiple files to process at the same time. The files currently need to be in xlsx or csv format, and the content needs to be in a table format.
2. x_axis_name: The name of the horizontal axis of the output chart. After AI judgment, if the name is consistent with the meaning of the original table's column name, it will be changed to the original table's column name.
3. y_axis_name: The name of the vertical axis of the output chart. After AI judgment, if the name is consistent with the meaning of the original table's column name, it will be changed to the original table's column name.
4. instruction: The user's goal, such as calculating the sales volume of each region, or calculating the proportion of sales volume of each region to the total sales volume.

The final flow will output a chart. The horizontal and vertical axis names of the chart are specified by the user, and the content of the chart is generated according to the user's instructions. AI will generate code based on user instructions and then execute the code to generate the chart.
If the code execution fails, the flow will automatically modify the code and retry 3 times.
