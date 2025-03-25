import os
import tempfile
import pandas as pd
from typing import List, Tuple
import glob
import subprocess
from langchain.tools import Tool, StructuredTool
from langchain_community.chat_models import ChatOpenAI

from .models import ReadFileRequest, GenerateAnalysisCodeRequest, ExecuteCodeRequest

def read_data_file(file_path: str) -> str:
    """Reads a data file and returns a description."""
    try:
        if file_path.endswith(('.csv')):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            return f"Error: Unsupported file format: {file_path}"
        
        # Create a more detailed description
        info_str = f"Successfully read data from {file_path}.\n\n"
        info_str += f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns\n\n"
        
        # Data types
        info_str += "Data Types:\n"
        for col, dtype in df.dtypes.items():
            info_str += f"- {col}: {dtype}\n"
        info_str += "\n"
        
        # Missing values
        missing = df.isnull().sum()
        info_str += "Missing Values:\n"
        for col, count in missing.items():
            percentage = (count / len(df)) * 100
            info_str += f"- {col}: {count} ({percentage:.2f}%)\n"
        info_str += "\n"
        
        # First 5 rows
        info_str += "First 5 rows:\n"
        info_str += df.head().to_string()
        
        return info_str
    except Exception as e:
        return f"Error reading file: {e}"

def execute_python_code(code: str) -> Tuple[str, List[str]]:
    """Executes Python code and captures output and any data file paths."""
    temp_file = None
    plot_files = []
    try:
        # Ensure eda_plots directory exists
        os.makedirs('./eda_plots', exist_ok=True)
        
        # Clean up any existing plot files in the eda_plots directory
        plot_extensions = ['.png', '.jpg', '.jpeg']
        for ext in plot_extensions:
            files_to_remove = glob.glob(f'eda_plots/*{ext}')
            for file in files_to_remove:
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Warning: Could not remove file {file}: {e}")
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
            tmp_file.write(code)
            temp_file = tmp_file.name

        process = subprocess.Popen(['python3', temp_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if stderr:
            # Evaluate the error and provide detailed guidance
            error_info = f"Error during code execution:\n{stderr}\n\n"
            error_info += "ERROR EVALUATION:\n"
            
            # Identify error type and location
            error_lines = stderr.strip().split('\n')
            error_type = "Unknown"
            error_line = "Unknown"
            error_message = "Unknown"
            
            # Extract error type, line number, and message
            for line in error_lines:
                if "line" in line and ".py" in line:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        error_line = parts[1].strip()
                if "Error:" in line or "Exception:" in line:
                    error_parts = line.split(':', 1)
                    if len(error_parts) >= 2:
                        error_type = error_parts[0].strip()
                        error_message = error_parts[1].strip()
            
            error_info += f"Error Type: {error_type}\n"
            error_info += f"Error Location: {error_line}\n"
            error_info += f"Error Message: {error_message}\n\n"
            
            # Add specific guidance for common errors
            if "FutureWarning" in stderr and "inplace" in stderr:
                error_info += "GUIDANCE: The code is using 'inplace=True' in pandas operations, which is deprecated. "
                error_info += "Replace these operations with assignment, e.g., 'df = df.dropna()' instead of 'df.dropna(inplace=True)'.\n\n"
            
            if "ValueError: Feature names mismatch" in stderr:
                error_info += "GUIDANCE: The model was trained with different features than what you're providing for prediction. "
                error_info += "Ensure the prediction sample has exactly the same features (columns) as the training data, "
                error_info += "including any one-hot encoded or transformed features.\n\n"
            
            if "could not convert string to float" in stderr:
                error_info += "GUIDANCE: There's a data type conversion issue. Ensure all numeric columns are properly converted "
                error_info += "using pd.to_numeric() with errors='coerce' and handle missing values appropriately.\n\n"
            
            if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
                error_info += "GUIDANCE: The code is trying to import a module that is not available. "
                error_info += "Check the import statements and ensure all required libraries are properly imported. "
                error_info += "Common issues include typos in import names or using libraries that require installation.\n\n"
            
            if "SyntaxError" in stderr:
                error_info += "GUIDANCE: There's a syntax error in the code. "
                error_info += "Check for missing parentheses, brackets, colons, or other syntax elements. "
                error_info += "Also check for indentation issues, especially in functions, loops, or conditional statements.\n\n"
            
            if "KeyError" in stderr:
                error_info += "GUIDANCE: The code is trying to access a key that doesn't exist in a dictionary or a column that doesn't exist in a DataFrame. "
                error_info += "Check the column names and ensure they match exactly with what's in the dataset. "
                error_info += "Remember that column names are case-sensitive.\n\n"
            
            if "FileNotFoundError" in stderr:
                error_info += "GUIDANCE: The code is trying to access a file that doesn't exist. "
                error_info += "Check the file path and ensure it's correct. "
                error_info += "Use relative paths (e.g., 'data/file.csv') rather than absolute paths.\n\n"
            
            if "TypeError" in stderr and "NoneType" in stderr:
                error_info += "GUIDANCE: The code is trying to perform an operation on a None value. "
                error_info += "This often happens when a function returns None unexpectedly. "
                error_info += "Add checks to ensure variables are not None before using them.\n\n"
            
            error_info += "RECOMMENDED ACTIONS:\n"
            error_info += "1. Carefully review the error message and location\n"
            error_info += "2. Check the specific line of code mentioned in the error\n"
            error_info += "3. Apply the guidance provided above to fix the issue\n"
            error_info += "4. Use the generate_data_analysis_code tool to create fixed code\n"
            error_info += "5. Use the execute_python_code tool to run the fixed code\n\n"
            
            error_info += "You MUST fix these errors and try again. DO NOT terminate the chain until the task is completed successfully."
            
            return error_info, []
        else:
            # Collect generated plot files
            if os.path.exists('eda_plots'):
                for f in os.listdir('eda_plots'):
                    if f.endswith((".png", ".jpg", ".jpeg")):
                        plot_files.append(os.path.join('eda_plots', f))
                        
            # If no plots found in eda_plots, check current directory as fallback
            if not plot_files:
                for f in os.listdir('.'):
                    if f.endswith((".png", ".jpg", ".jpeg")):
                        plot_files.append(f)
                        
                # If plots found in current directory, move them to eda_plots
                for f in plot_files:
                    os.rename(f, os.path.join('eda_plots', os.path.basename(f)))
                    
            result = f"Code executed successfully.\n\n"
            
            if stdout:
                result += f"Output:\n{stdout}\n\n"
            
            if plot_files:
                result += f"Generated {len(plot_files)} plot files:\n"
                for plot in plot_files:
                    result += f"- {plot}\n"
            else:
                result += "No plot files were generated."
            
            return result, plot_files
    except Exception as e:
        detailed_error = f"Error executing code: {e}\n\n"
        detailed_error += "ERROR EVALUATION:\n"
        detailed_error += f"Error Type: {type(e).__name__}\n"
        detailed_error += f"Error Message: {str(e)}\n\n"
        
        detailed_error += "RECOMMENDED ACTIONS:\n"
        detailed_error += "1. Check if the code has syntax errors\n"
        detailed_error += "2. Ensure all required libraries are imported\n"
        detailed_error += "3. Verify file paths and data access methods\n"
        detailed_error += "4. Add error handling with try/except blocks\n"
        detailed_error += "5. Use the generate_data_analysis_code tool to create fixed code\n\n"
        
        detailed_error += "You MUST fix this error and try again. DO NOT terminate the chain until the task is completed successfully."
        
        return detailed_error, []
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

def generate_data_analysis_code(file_path: str, analysis_objective: str, model: str) -> str:
    """Generates Python code for data analysis based on the file and objective."""
    prompt = f"""
Generate comprehensive Python code for {analysis_objective} on the data in '{file_path}'. 

The code should:
1. Import all necessary libraries (pandas, numpy, matplotlib, seaborn, scipy, sklearn, etc.)
2. Create a directory named 'eda_plots' if it doesn't exist
3. Clear any existing plot files in the eda_plots directory
4. Load the data from '{file_path}'
5. Perform data cleaning and preprocessing
6. Perform the specific analysis requested in the objective
7. Save visualizations to the 'eda_plots' directory
8. Print a summary of findings

CRITICAL REQUIREMENTS FOR CODE GENERATION:
1. DO NOT use inplace=True in pandas operations - use assignment instead (e.g., df = df.dropna() instead of df.dropna(inplace=True))
2. When making predictions with a model, ensure the features match exactly what the model was trained with
3. Handle data type conversions safely using pd.to_numeric() with errors='coerce'
4. Handle missing values appropriately
5. Use try/except blocks to catch and handle errors
6. Use tight_layout() for all plots
7. Print detailed insights that can be included in the final report
8. Ensure all file paths are correct and use relative paths
9. Check for and handle edge cases (empty dataframes, unexpected data types, etc.)
10. Add comments explaining complex operations
11. Clear any existing plot files in the eda_plots directory at the start of execution

COMPREHENSIVE EDA REQUIREMENTS:
1. ALWAYS generate ALL of the following visualizations and analyses, regardless of the specific objective:
   a. Distribution plots for all numeric columns (histograms, KDE plots, box plots)
   b. Count plots for all categorical columns
   c. Correlation heatmap for all numeric columns
   d. Pairplots for key numeric features (limit to 5-8 most important features if there are many)
   e. Time series plots for any datetime columns
   f. Missing value analysis and visualization
   g. Outlier detection and visualization
   h. Statistical summaries (mean, median, mode, std, min, max, quartiles) for all numeric columns
   i. Frequency analysis for categorical columns
   j. Bivariate analysis between target (if identified) and other features

2. For each visualization:
   a. Use appropriate color palettes and styling to maximize readability
   b. Include proper titles, labels, and annotations
   c. Save with high resolution (dpi=300)
   d. Use descriptive filenames that clearly indicate what is being visualized
   e. Add plt.tight_layout() to ensure proper formatting

3. Print detailed insights about:
   a. Key patterns and trends observed in the data
   b. Statistical significance of relationships
   c. Potential feature importance
   d. Anomalies or interesting findings

CRITICAL PLOT GENERATION REQUIREMENTS:
1. You MUST include the following code at the beginning to ensure plots are saved correctly:
```python
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Create eda_plots directory if it doesn't exist
os.makedirs('./eda_plots', exist_ok=True)

# Set up plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")
```

2. For EVERY plot you create, you MUST include code to save it to the eda_plots directory like this:
```python
# Example for saving a histogram
plt.figure(figsize=(12, 8))
sns.histplot(data=df, x='column_name', kde=True)
plt.title('Distribution of Column Name')
plt.tight_layout()
plt.savefig('./eda_plots/column_name_distribution.png', dpi=300)
plt.close()
```

3. ALWAYS use plt.savefig() BEFORE plt.show() if you include plt.show()

4. ALWAYS include plt.close() after saving each plot to prevent memory issues

5. ALWAYS use the './eda_plots/' directory prefix in all savefig() calls

6. ALWAYS use descriptive filenames that indicate what the plot represents

Only when prompted to, if you're implementing a machine learning model:
1. Ensure proper feature engineering and selection
2. Split data appropriately into training and testing sets
3. Evaluate the model thoroughly
4. When making predictions for specific cases, ensure the input features match exactly what the model was trained with
5. Print detailed results and insights

The code must be complete, well-structured, and ready to execute without any modifications.
"""
    
    llm = ChatOpenAI(model=model)
    return llm.predict(prompt)

def create_tools(model: str):
    """Creates and returns the tools for the agent."""
    tools = [
        Tool(
            name="read_data_file",
            func=read_data_file,
            description="Reads a data file (CSV or Excel) and returns detailed information about its structure, columns, data types, and first few rows. ALWAYS use this tool FIRST to understand the dataset before generating any analysis code. This information is crucial for planning your comprehensive EDA.",
            args_schema=ReadFileRequest
        ),
        StructuredTool(
            name="generate_data_analysis_code",
            func=lambda file_path, analysis_objective: generate_data_analysis_code(file_path, analysis_objective, model),
            description="Generates comprehensive Python code for data analysis based on the file and objective. The code will include data loading, preprocessing, visualization, and saving plots to the 'eda_plots' directory. The code MUST generate ALL possible visualizations and analyses, including distribution plots, correlation heatmaps, pairplots, time series plots, missing value analysis, outlier detection, and statistical summaries for all columns. Use this tool AFTER reading the data file. If code execution fails, use this tool again to generate fixed code.",
            args_schema=GenerateAnalysisCodeRequest
        ),
        Tool(
            name="execute_python_code",
            func=execute_python_code,
            description="Executes the generated Python code and returns the output along with paths to any generated plot files. Use this tool AFTER generating the analysis code to run the analysis and create ALL required visualizations. If execution fails, the tool will provide detailed error evaluation and guidance for fixing the issues. You MUST fix any errors and try again until the task is completed successfully with ALL required visualizations and analyses generated.",
            args_schema=ExecuteCodeRequest
        )
    ]
    return tools