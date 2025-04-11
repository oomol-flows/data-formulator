# data-formulator

This project is modified from [microsoft/data-formulator](https://github.com/microsoft/data-formulator).

This project is designed to analyze tabular data uploaded by users and output customized formatted data according to user preferences.
It uses AI to analyze user intent, translates the intent into code, and executes the code to generate the desired formatted data, which is then displayed in graphical form.

The input file format should be a two-dimensional table. Complex header structures may lead to inaccurate results. Please organize the headers yourself.

## Flow
###  process-xlsx-data-and-display-chart

Receives an xlsx file, formats its content according to user requirements, and displays it as a chart. The flow has the following inputs:
![flow](flow.jpeg)

1. input: The file path, currently requiring an xlsx format with tabular content.
2. instruction: The user's goal, such as calculating sales by region or the proportion of sales per region to total sales.
3. x_axis_name: The name of the x-axis in the output chart. If the AI determines it matches the original table's column name, it will use the original column name.
4. y_axis_name: The name of the y-axis in the output chart. If the AI determines it matches the original table's column name, it will use the original column name.

The flow outputs a chart with user-specified axis names and content generated based on the user's instructions. The AI generates code to produce the chart.
If the code fails, the flow automatically modifies the code and retries once.

## Shared Block
* derive-data
Users can specify the axis names and custom requirements for the output table. The AI determines how to meet the requirements, generates code, and executes it to output the desired chart data structure.
Code execution failure triggers automatic modification and retries once.

* summarize-data
Summarizes input data (array format), describing what the input records and automatically determining the data format.