from pydantic import BaseModel, Field
from typing import List

# Pydantic Models for Tool Input
class ReadFileRequest(BaseModel):
    file_path: str = Field(description="The path to the data file.")

class GenerateAnalysisCodeRequest(BaseModel):
    file_path: str = Field(description="The path to the data file.")
    analysis_objective: str = Field(description="The objective of the request (e.g., answer).")

class ExecuteCodeRequest(BaseModel):
    code: str = Field(description="The Python code to execute.")

class AnalyzeResultsRequest(BaseModel):
    code_output: str = Field(description="The output from executing the code.")
    plot_files: List[str] = Field(description="List of paths to the generated useful data.")

class CreateReportRequest(BaseModel):
    analysis: str = Field(description="The analysis of the results.")
    plot_files: List[str] = Field(description="List of paths to the generated data files.")