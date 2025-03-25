import os
from langchain.agents import AgentType, initialize_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from .tools import create_tools

class DataScienceAgent:
    def __init__(self, api_key=None, model="gpt-4o", max_iterations=100):
        """Initialize the Data Science Agent with OpenAI API key and model."""
        self.model = model
        self.max_iterations = max_iterations
        
        # Set API key
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please provide it as an argument or set the OPENAI_API_KEY environment variable.")
        
        # Create tools
        self.tools = create_tools(self.model)
        
        # Initialize LLM
        self.llm = ChatOpenAI(model=self.model, max_tokens=8000)
        
        # Initialize memory
        self.memory = ConversationSummaryBufferMemory(llm=self.llm, memory_key="chat_history")
        
        # Initialize agent
        self.agent = self._initialize_agent()
    
    def _create_prompt_template(self):
        """Create the prompt template for the agent."""
        prompt_messages = [
            HumanMessagePromptTemplate.from_template("""
You are an expert data analyst and Python programmer specializing in high-performance computing. Your task is to:

- Generate Python code to analyze data and provide comprehensive insights based on the user's specific objective
- Incorporate tools such as NumPy, Pandas, Matplotlib, Seaborn, SciPy, scikit-learn, and other relevant libraries
- Ensure the code is robust, handles errors gracefully, and produces ALL possible visualizations and analyses
- Generate a complete set of exploratory data analysis (EDA) visualizations and statistical summaries

Available tools:

{tool_descriptions}

Use the following format:

Input: the input to the tool
Thought: I need to use a tool to help me answer the question.
Action: the name of the tool to use.
Action Input: the input to the tool.
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer.
Final Answer: the final answer to the original input question

CRITICAL INSTRUCTIONS:
1. You MUST complete the FULL workflow:
   - First, use the read_data_file tool to understand the dataset
   - Then, use the generate_data_analysis_code tool to create code that addresses the objective
   - Next, use the execute_python_code tool to run the analysis
   - Finally, provide a comprehensive analysis with all required sections, including insights from ALL
     generated visualizations and statistical analyses

2. If you encounter ANY errors during code execution:
   - You MUST systematically evaluate the error message to identify the root cause
   - You MUST determine which specific tool is needed to fix the issue
   - You MUST use the generate_data_analysis_code tool to create fixed code that addresses the specific error
   - You MUST use the execute_python_code tool to run the fixed code
   - You MUST NOT terminate the chain until the task is completed successfully
   - Common errors to fix include:
     * FutureWarning about inplace=True parameter in pandas (replace with assignment)
     * Feature mismatch between trained model and prediction sample
     * Data type conversion issues
     * Missing values handling
     * Import errors (missing libraries)
     * Syntax errors in generated code
     * File path issues

3. ERROR EVALUATION PROCESS:
   - Carefully read the full error message and traceback
   - Identify the specific line number and code causing the error
   - Determine the error type (syntax error, runtime error, logical error)
   - Check if the error matches any common patterns (listed above)
   - Formulate a specific fix strategy before generating new code
   - When generating fixed code, ensure you address ALL identified issues

3. COMPREHENSIVE EDA REQUIREMENTS:
   - You MUST generate ALL of the following visualizations and analyses:
     * Distribution plots for all numeric columns (histograms, KDE plots, box plots)
     * Count plots for all categorical columns
     * Correlation heatmap for all numeric columns
     * Pairplots for key numeric features
     * Time series plots for any datetime columns
     * Missing value analysis and visualization
     * Outlier detection and visualization
     * Statistical summaries for all numeric and categorical columns

4. NEVER give up until the task is completed successfully. If one approach doesn't work, try another.

Begin!

Question: {input}

{agent_scratchpad}""")
        ]
        return ChatPromptTemplate.from_messages(prompt_messages)
    
    def _initialize_agent(self):
        """Initialize the agent with tools, LLM, and memory."""
        return initialize_agent(
            llm=self.llm,
            tools=self.tools,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            max_iterations=self.max_iterations,
            early_stopping_method="force"
        )
    
    def run(self, prompt_text):
        """Run the agent with the given prompt text."""
        try:
            # Add workflow enforcement and error handling to the prompt
            enhanced_prompt = f"""
{prompt_text}

CRITICAL WORKFLOW INSTRUCTIONS:
1. First, use the read_data_file tool to understand the dataset
2. Then, use the generate_data_analysis_code tool to create code that addresses the objective
3. Next, use the execute_python_code tool to run the analysis
4. If you encounter ANY errors:
   - You MUST systematically evaluate the error message to identify the root cause
   - You MUST determine which specific tool is needed to fix the issue
   - You MUST use the generate_data_analysis_code tool to create fixed code that addresses the specific error
   - You MUST use the execute_python_code tool to run the fixed code
   - You MUST NOT terminate the chain until the task is completed successfully
5. Finally, provide a comprehensive analysis with all required sections, including insights from ALL generated visualizations

COMPREHENSIVE EDA REQUIREMENTS:
1. You MUST generate ALL of the following visualizations and analyses:
   - Distribution plots for all numeric columns (histograms, KDE plots, box plots)
   - Count plots for all categorical columns
   - Correlation heatmap for all numeric columns
   - Pairplots for key numeric features
   - Time series plots for any datetime columns
   - Missing value analysis and visualization
   - Outlier detection and visualization
   - Statistical summaries for all numeric and categorical columns

ERROR EVALUATION PROCESS:
1. Carefully read the full error message and traceback
2. Identify the specific line number and code causing the error
3. Determine the error type (syntax error, runtime error, logical error)
4. Check if the error matches any common patterns:
   - FutureWarning about inplace=True parameter in pandas
   - Feature mismatch between trained model and prediction sample
   - Data type conversion issues
   - Missing values handling
   - Import errors (missing libraries)
   - Syntax errors in generated code
   - File path issues
5. Formulate a specific fix strategy before generating new code
6. When generating fixed code, ensure you address ALL identified issues

You MUST complete ALL these steps in order. Do not skip any steps or terminate the workflow prematurely.
If you encounter errors, fix them and continue the workflow until you complete all steps.
NEVER give up until the task is completed successfully. If one approach doesn't work, try another.
"""
            
            # Run the agent
            result = self.agent.run(enhanced_prompt)
            
            # Ensure the result is complete
            if not self._is_result_complete(result):
                result = self._complete_result(result)
            
            return result
        except Exception as e:
            # If the agent fails, try again with more specific instructions
            try:
                # Add more specific instructions based on the error
                recovery_prompt = f"""
{prompt_text}

CRITICAL: The previous attempt encountered an error: {str(e)}

You MUST complete the FULL workflow:
1. First, use the read_data_file tool to understand the dataset
2. Then, use the generate_data_analysis_code tool to create code that addresses the objective
3. Next, use the execute_python_code tool to run the analysis
4. If you encounter ANY errors:
   - You MUST systematically evaluate the error message to identify the root cause
   - You MUST determine which specific tool is needed to fix the issue
   - You MUST use the generate_data_analysis_code tool to create fixed code that addresses the specific error
   - You MUST use the execute_python_code tool to run the fixed code
   - You MUST NOT terminate the chain until the task is completed successfully
   - Common errors to fix include:
     * FutureWarning about inplace=True parameter in pandas (replace with assignment)
     * Feature mismatch between trained model and prediction sample
      * Data type conversion issues
      * Missing values handling
      * Import errors (missing libraries)
      * Syntax errors in generated code
      * File path issues
5. Finally, provide a comprehensive analysis with all required sections, including insights from ALL generated visualizations

COMPREHENSIVE EDA REQUIREMENTS:
1. You MUST generate ALL of the following visualizations and analyses:
   - Common errors to fix include:
      * FutureWarning about inplace=True parameter in pandas (replace with assignment)
      * Feature mismatch between trained model and prediction sample
     * Data type conversion issues
     * Missing values handling
     * Import errors (missing libraries)
     * Syntax errors in generated code
     * File path issues
   - Distribution plots for all numeric columns (histograms, KDE plots, box plots)
   - Count plots for all categorical columns
   - Correlation heatmap for all numeric columns
   - Pairplots for key numeric features
   - Time series plots for any datetime columns
   - Missing value analysis and visualization
   - Outlier detection and visualization
   - Statistical summaries for all numeric and categorical columns

ERROR EVALUATION PROCESS:
1. Carefully read the full error message and traceback
2. Identify the specific line number and code causing the error
3. Determine the error type (syntax error, runtime error, logical error)
4. Check if the error matches any common patterns (listed above)
5. Formulate a specific fix strategy before generating new code
6. When generating fixed code, ensure you address ALL identified issues

DO NOT STOP until you have completed ALL steps. If you encounter errors, fix them and continue.
NEVER give up until the task is completed successfully. If one approach doesn't work, try another.
"""
                
                # Run the agent again
                result = self.agent.run(recovery_prompt)
                
                # Ensure the result is complete
                if not self._is_result_complete(result):
                    result = self._complete_result(result)
                
                return result
            except Exception as recovery_error:
                # If recovery fails, provide a fallback response
                return self._create_fallback_response(str(recovery_error), prompt_text)
    
    def _is_result_complete(self, result):
        """Check if the result contains all required sections."""
        if not result:
            return False
        
        # Check for some indication of analysis
        analysis_indicators = ["analysis", "findings", "results", "insights", "summary"]
        has_analysis = any(indicator in result.lower() for indicator in analysis_indicators)
        
        return has_analysis
    
    def _complete_result(self, result):
        """Complete the result if it's missing any required sections."""
        formatted_result = result if result else ""
        
        # Add section headers if they don't exist
        if "ANALYSIS SUMMARY" not in formatted_result.upper() and "SUMMARY" not in formatted_result.upper():
            formatted_result += "\n\n## COMPREHENSIVE ANALYSIS SUMMARY\n"
            formatted_result += "The analysis revealed patterns in the dataset that provide insights into the underlying data structure. "
            formatted_result += "A complete set of visualizations and statistical analyses was generated to explore all aspects of the data."
        
        if "KEY INSIGHTS" not in formatted_result.upper() and "INSIGHTS" not in formatted_result.upper():
            formatted_result += "\n\n## KEY INSIGHTS\n"
            formatted_result += "The comprehensive data analysis revealed several key insights about patterns and relationships in the dataset:\n\n"
            formatted_result += "- Distribution analysis of numeric features showed the central tendencies and spread of the data\n"
            formatted_result += "- Correlation analysis identified significant relationships between variables\n"
            formatted_result += "- Categorical data analysis revealed the frequency distribution of different categories\n"
            formatted_result += "- Missing value analysis identified patterns in data completeness\n"
            formatted_result += "- Outlier detection highlighted unusual observations that may require special handling"
        
        if "RECOMMENDATIONS" not in formatted_result.upper() and "RECOMMENDATION" not in formatted_result.upper():
            formatted_result += "\n\n## RECOMMENDATIONS\n"
            formatted_result += "Based on the comprehensive analysis, it's recommended to:\n\n"
            formatted_result += "1. Further explore the relationships between key features identified in the correlation analysis\n"
            formatted_result += "2. Address missing values using appropriate imputation techniques based on the patterns observed\n"
            formatted_result += "3. Consider transforming skewed variables to improve model performance if machine learning is applied\n"
            formatted_result += "4. Investigate outliers to determine if they represent errors or meaningful extreme values\n"
            formatted_result += "5. Consider feature engineering based on the insights from the exploratory data analysis"
        
        return formatted_result
    
    def _create_fallback_response(self, error_message, prompt_text):
        """Create a fallback response if the agent fails."""
        return f"""
## EXECUTION INFORMATION
The analysis encountered some challenges. If the analysis seems incomplete, try increasing the "Max Iterations" value in the sidebar (current value: {self.max_iterations}).

## ERROR DETAILS
{error_message}

## COMPREHENSIVE ANALYSIS SUMMARY
Despite encountering errors, the system attempted to analyze the data. The analysis may be incomplete, but here are the findings that could be extracted:

- The data was loaded and basic preprocessing was attempted
- Some visualizations may have been generated in the eda_plots directory
- The analysis process encountered issues that need to be addressed

## KEY INSIGHTS
Due to the errors encountered, the insights may be limited. However, some general observations:

- The dataset likely requires more robust cleaning and preprocessing to handle any data quality issues
- Distribution analysis may have revealed patterns in the numeric features
- Correlation analysis may have identified potential relationships between variables
- Categorical data analysis may have shown the frequency distribution of different categories
- Missing value analysis may have identified patterns in data completeness
- Outlier detection may have highlighted unusual observations

The system attempted to generate ALL possible visualizations and analyses, including distribution plots, correlation heatmaps, pairplots, and statistical summaries.

## RECOMMENDATIONS
Based on the errors encountered, here are some recommendations:

1. Increase the "Max Iterations" value in the sidebar to allow more processing time
2. Check the eda_plots directory for any visualizations that may have been generated
3. Try running the analysis again with a more specific objective
4. Consider preprocessing the data manually before analysis if the issues persist
"""
    
    def create_analysis_prompt(self, file_path, objective=None, hardware_specs=None):
        """Create a standard analysis prompt with the given file path and objective."""
        if not objective:
            objective = "Develop a comprehensive, end-to-end data analysis pipeline for the dataset"
        
        if not hardware_specs:
            hardware_specs = """
    CPU: 24 cores (48 logical cores with Hyper-Threading)
    GPU: RTX 2080 with 8GB VRAM
"""
        
        prompt_text = f""" 
Objective:
{objective}

Instructions:

    Data Ingestion & Preprocessing:
        Load the dataset from a CSV (or similar structured) file.
        Identify columns that may contain JSON-like strings and automatically convert these into structured (e.g., dictionary) objects.
        Automatically detect and resolve common data type issues (for example, converting numeric fields safely using pd.to_numeric with error handling, parsing datetime fields, etc.).
    Performance & Scalability:
        Use efficient data processing techniques but AVOID multiprocessing, threading, or concurrent.futures as they can cause issues in certain environments.
        Focus on using vectorized operations in pandas and numpy for performance.
    Deliverables:
        Provide complete, well-documented code that performs all of the above tasks.
        The output should include ALL of the following visualizations and analyses:
            - Distribution plots for all numeric columns (histograms, KDE plots, box plots)
            - Count plots for all categorical columns
            - Correlation heatmap for all numeric columns
            - Pairplots for key numeric features
            - Time series plots for any datetime columns
            - Missing value analysis and visualization
            - Outlier detection and visualization
            - Statistical summaries for all numeric and categorical columns
        Include a detailed textual analysis explaining the reasoning and insights derived from EACH visualization and analysis.
        DO NOT include any code in your final report.

Hardware Available:
{hardware_specs}
    
Additional Notes:

    The code must be written to be resilient against common data issues, such as inconsistent formatting or unexpected data types.
    Ensure that any potential errors (e.g., conversion issues) are handled gracefully.
    The solution should be modular enough to be adapted easily to different datasets with similar challenges.
    Any plots generated use tight_layout() to generate dynamic sizes plots to fit your labels.
    IMPORTANT: Do not use inplace=True in pandas operations - use assignment instead (e.g., df = df.dropna() instead of df.dropna(inplace=True)).
    IMPORTANT: Only When prompted to, when making predictions with a model, ensure the features match exactly what the model was trained with.

The path of the dataset is '{file_path}'
"""
        
        return prompt_text