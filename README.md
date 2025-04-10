# data-formulator

This project is modified from [microsoft/data-formulator](https://github.com/microsoft/data-formulator).

This project is designed to analyze tabular data uploaded by users and output customized formatted data according to user preferences.
It uses AI to analyze user intent, translates the intent into code, and executes the code to generate the desired formatted data, which is then displayed in graphical form.

## Flow
* process-xlsx-data-and-display-chart
Receives an xlsx file, formats its content according to user requirements, and displays it in chart form.

## Shared Block
* derive-data
Users can specify the names of the horizontal and vertical axes of the output table and customize requirements. AI will determine how to meet the requirements based on the input data, generate code, and automatically execute it, ultimately outputting the chart data structure that meets user requirements.

* summarize-data
Summarizes input data (array format), roughly describes what the input records, and automatically determines the format of the input data.