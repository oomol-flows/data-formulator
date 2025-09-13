# Data Formulator 📊

Transform your data into beautiful visualizations with AI-powered analysis! Data Formulator is an intelligent workflow platform that helps you analyze spreadsheet data and create meaningful charts without any programming knowledge.

## What is Data Formulator?

Data Formulator is a no-code data analysis tool that automatically processes your Excel or CSV files and generates interactive charts based on your questions or goals. Simply upload your data, describe what you want to analyze, and let AI do the heavy lifting!

## Key Features

✨ **AI-Powered Analysis** - Understands your data analysis goals in plain English  
📊 **Automatic Chart Generation** - Creates the most appropriate visualizations for your data  
📁 **Multiple File Support** - Works with CSV and Excel files  
🎨 **Interactive Visualizations** - Generate charts you can interact with and customize  
🔧 **No Coding Required** - Perfect for business users, researchers, and analysts

## Building Blocks

Data Formulator consists of several specialized blocks that work together to analyze your data:

### 📥 Read Files Block
**What it does:** Loads your CSV or Excel files into the system  
**When to use:** Always start here - this is how you get your data into the workflow  
**Features:**
- Supports multiple file formats (CSV, XLSX)
- Automatic data preview
- Handles multiple files at once

### 🧠 AI Data Analysis Block (Subflow)
**What it does:** The main intelligence of the system - analyzes your data based on your instructions  
**When to use:** After loading your files, this is where the magic happens  
**Features:**
- Understands natural language instructions
- Automatically selects appropriate analysis methods
- Generates insights and prepares data for visualization

### 🔍 Derive Data Block
**What it does:** Transforms and extracts specific insights from your datasets  
**When to use:** When you need to calculate new metrics or filter data based on conditions  
**Features:**
- AI-powered data transformations
- Custom calculations and filtering
- Automatic code generation for data processing

### 📈 Result Chart Block
**What it does:** Creates beautiful, interactive charts from your analyzed data  
**When to use:** Final step to visualize your results  
**Supported Chart Types:**
- Bar charts
- Line graphs  
- Scatter plots
- Pie charts
- Histograms
- Box plots
- Area charts
- Radar charts
- Heat maps
- Violin plots
- Bubble charts

### 📝 Summarize Data Block
**What it does:** Generates comprehensive statistical summaries of your datasets  
**When to use:** When you need an overview of your data's key statistics  
**Features:**
- Automatic statistical analysis
- Data quality assessment
- Field schema generation

### 👁️ Code Preview Block
**What it does:** Shows you the Python code that was automatically generated for your analysis  
**When to use:** When you want to understand or verify the analysis process  
**Features:**
- Clean, readable code display
- Educational tool for learning data analysis

## How to Use Data Formulator

### Step 1: Prepare Your Data
- Save your data as a CSV or Excel file
- Ensure your data has clear column headers
- Clean up any obvious data quality issues

### Step 2: Upload Your File
1. Use the **Read Files Block** to upload your data
2. Enable preview to see your data structure
3. Verify that the data loaded correctly

### Step 3: Define Your Analysis Goal
1. Add the **AI Data Analysis Block** to your workflow
2. Connect your uploaded data to this block
3. Write your analysis instruction in plain English, for example:
   - "Show me the relationship between sales and marketing spend"
   - "What percentage of customers have IQ scores above 120?"
   - "Compare performance across different regions"

### Step 4: Generate Visualizations
The system will automatically:
- Analyze your instruction
- Process your data accordingly
- Generate the most appropriate chart type
- Display interactive results

## Example Use Cases

### 📊 Business Analytics
- **Sales Performance:** "Compare quarterly sales across different product lines"
- **Customer Analysis:** "Show the distribution of customer ages by region"
- **Marketing ROI:** "Analyze the correlation between ad spend and conversions"

### 🎓 Academic Research
- **Survey Analysis:** "What's the relationship between study hours and test scores?"
- **Demographic Studies:** "Compare income levels across education categories"
- **Experimental Results:** "Show the effect of treatment groups on outcome variables"

### 📈 Personal Finance
- **Expense Tracking:** "Break down my monthly expenses by category"
- **Investment Analysis:** "Show the performance of my portfolio over time"
- **Budget Planning:** "Compare actual vs planned spending"

## Tips for Better Results

### Writing Good Instructions
- **Be specific:** Instead of "analyze sales," try "show monthly sales trends for 2023"
- **Include context:** Mention what you're looking for - trends, comparisons, distributions
- **Specify axes:** If you have preferences for X and Y axes, mention them

### Data Preparation
- **Clean headers:** Use clear, descriptive column names
- **Consistent formatting:** Ensure dates, numbers, and categories are formatted consistently
- **Remove empty rows:** Clean up your data before uploading

### Chart Selection
- **Let AI choose:** The system usually picks the best chart type automatically
- **Override when needed:** You can specify a particular chart type if you prefer
- **Consider your audience:** Think about who will view the charts

## Getting Started

1. **Download the sample data** from the `/oomol-driver/oomol-storage/` directory
2. **Create a new workflow** using the AI Data Analysis subflow
3. **Upload your data** using the Read Files block
4. **Write your analysis goal** in the instruction field
5. **Run the workflow** and see your results!

## Technical Requirements

- **File Formats:** CSV, XLSX (Excel)
- **Data Size:** Works with datasets of various sizes
- **Languages:** Supports analysis instructions in multiple languages
- **Output:** Interactive charts and statistical summaries

## Support

If you encounter any issues or have questions:
- Check that your data file is properly formatted
- Ensure your analysis instructions are clear and specific
- Verify that all blocks are properly connected in your workflow

---

*Data Formulator makes data analysis accessible to everyone. No programming skills required - just upload, describe, and discover insights in your data!* 🚀