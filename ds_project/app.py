import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import requests
from src.agent import DataScienceAgent

# Set page configuration
st.set_page_config(
    page_title="Data Science Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def fetch_available_models(api_key):
    """Fetch available models from OpenAI API based on the provided API key."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.openai.com/v1/models", headers=headers)
        
        if response.status_code == 200:
            models_data = response.json()
            
            # Get all models
            all_models = [model['id'] for model in models_data['data']]
            
            # Display all models for debugging
            st.write("### All Available Models:")
            for model in all_models:
                st.write(f"- {model}")
            
            # No filtering - show all models
            sorted_models = sorted(all_models,
                                  key=lambda x: (
                                      # Sort by model family (gpt-4 first, then gpt-3.5)
                                      0 if 'gpt-4' in x.lower() else
                                      1 if 'gpt-3.5' in x.lower() else
                                      2 if 'text-davinci' in x.lower() else 3
                                  ))
            
            return sorted_models if sorted_models else ["gpt-3.5-turbo"]  # Fallback to a default model
        else:
            st.warning(f"Failed to fetch models: {response.status_code} - {response.text}")
            return ["gpt-3.5-turbo"]  # Fallback to a default model
    except Exception as e:
        st.warning(f"Error fetching models: {e}")
        return ["gpt-3.5-turbo"]  # Fallback to a default model

# Initialize session state variables
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'available_models' not in st.session_state:
    st.session_state.available_models = ["gpt-3.5-turbo"]  # Default model
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gpt-3.5-turbo"  # Default model
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'plot_files' not in st.session_state:
    st.session_state.plot_files = []
if 'dataframe' not in st.session_state:
    st.session_state.dataframe = None

# Initialize max_iterations with a default value
if 'max_iterations' not in st.session_state:
    st.session_state.max_iterations = 100

def update_models():
    """Update the available models based on the provided API key."""
    if st.session_state.api_key:
        with st.spinner("Fetching available models..."):
            st.info("Querying OpenAI API for available models...")
            models = fetch_available_models(st.session_state.api_key)
            
            if models:
                st.success(f"Successfully retrieved {len(models)} models from OpenAI API")
                st.session_state.available_models = models
                
                # Set selected model to the first available model if current selection is not available
                if st.session_state.selected_model not in models:
                    st.session_state.selected_model = models[0]
                    st.info(f"Selected model set to: {models[0]}")
            else:
                st.error("No models were returned from the OpenAI API")

def initialize_agent():
    """Initialize the agent with the provided API key and selected model."""
    try:
        st.session_state.agent = DataScienceAgent(
            api_key=st.session_state.api_key,
            model=st.session_state.selected_model,
            max_iterations=st.session_state.max_iterations
        )
        st.success(f"Agent initialized successfully with model: {st.session_state.selected_model}!")
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.session_state.agent = None

def run_analysis():
    """Run the analysis with the provided parameters."""
    if not st.session_state.agent:
        st.error("Please initialize the agent first.")
        return
    
    if not st.session_state.file_path:
        st.error("Please provide a file path.")
        return
    
    try:
        # Load the dataframe for display
        if st.session_state.file_path.endswith('.csv'):
            st.session_state.dataframe = pd.read_csv(st.session_state.file_path)
        elif st.session_state.file_path.endswith(('.xlsx', '.xls')):
            st.session_state.dataframe = pd.read_excel(st.session_state.file_path)
        else:
            st.error(f"Unsupported file format: {st.session_state.file_path}")
            return
        
        # Create the analysis prompt
        prompt = st.session_state.agent.create_analysis_prompt(
            file_path=st.session_state.file_path,
            objective=st.session_state.objective,
            hardware_specs=st.session_state.hardware_specs
        )
        
        # Run the agent
        with st.spinner("Running analysis... This may take a while."):
            results = st.session_state.agent.run(prompt)
            st.session_state.analysis_results = results
            
            # Check for plot files in the eda_plots directory
            if os.path.exists("eda_plots"):
                st.session_state.plot_files = [
                    os.path.join("eda_plots", f) for f in os.listdir("eda_plots") 
                    if f.endswith((".png", ".jpg", ".jpeg"))
                ]
        
        st.success("Analysis completed!")
    except Exception as e:
        st.error(f"Error running analysis: {e}")

# Sidebar for configuration
with st.sidebar:
    st.title("Configuration")
    
    # API Key input
    api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
        # Update models when API key changes
        update_models()
    
    # Fetch models button
    if st.session_state.api_key:
        if st.button("Fetch Available Models"):
            update_models()
            st.success(f"Found {len(st.session_state.available_models)} models available to your API key")
        
        # Model selection dropdown
        st.subheader("Model Selection")
        st.write("Select a model to use for analysis:")
        
        model_options = st.session_state.available_models
        selected_model = st.selectbox(
            "Available Models",
            options=model_options,
            index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
        )
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.info(f"Selected model: {selected_model}")
    
    # Initialize agent button
    st.button("Initialize Agent", on_click=initialize_agent)
    
    # Agent configuration
    st.subheader("Agent Configuration")
    
    # Max iterations text input
    max_iterations = st.number_input(
        "Max Iterations",
        value=st.session_state.max_iterations,
        step=1,
        format="%d",
        help="Maximum number of iterations the agent can perform. Default is 100, which should be sufficient for most analyses. Increase this value if the agent is stopping before completing the analysis."
    )
    # Ensure max_iterations is at least 1
    if max_iterations < 1:
        st.warning("Max iterations must be at least 1. Setting to 1.")
        max_iterations = 1
        
    if max_iterations != st.session_state.max_iterations:
        st.session_state.max_iterations = max_iterations
        st.info(f"Max iterations set to: {max_iterations}")
    
    st.divider()
    
    # Analysis parameters
    st.subheader("Analysis Parameters")
    
    # File upload or path input
    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded_file:
        # Save the uploaded file
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.file_path = file_path
        st.success(f"File saved to {file_path}")
    
    # Or provide a file path
    file_path = st.text_input("Or provide a file path", value=st.session_state.get("file_path", ""))
    if file_path and file_path != st.session_state.get("file_path", ""):
        st.session_state.file_path = file_path
    
    # Analysis objective
    objective = st.text_area(
        "Analysis Objective",
        value=st.session_state.get("objective", "Develop a comprehensive, end-to-end data analysis pipeline for the dataset"),
        height=100
    )
    if objective != st.session_state.get("objective", ""):
        st.session_state.objective = objective
    
    # Hardware specifications
    hardware_specs = st.text_area(
        "Hardware Specifications",
        value=st.session_state.get("hardware_specs", """
CPU: 24 cores (48 logical cores with Hyper-Threading)
GPU: RTX 2080 with 8GB VRAM
"""),
        height=100
    )
    if hardware_specs != st.session_state.get("hardware_specs", ""):
        st.session_state.hardware_specs = hardware_specs
    
    # Run analysis button
    st.button("Run Analysis", on_click=run_analysis)

# Main content
st.title("Data Science Agent")
st.write("This application uses an AI agent to analyze data and generate insights.")

# Display agent status
if st.session_state.agent:
    st.success("Agent is initialized and ready to use.")
else:
    st.warning("Agent is not initialized. Please provide an OpenAI API key and initialize the agent.")

# Display DataFrame details if available
if st.session_state.dataframe is not None:
    st.header("DataFrame Details")
    
    # Display basic info
    st.subheader("Data Overview")
    st.write(f"Shape: {st.session_state.dataframe.shape[0]} rows, {st.session_state.dataframe.shape[1]} columns")
    
    # Display column info using StringIO
    st.subheader("Column Information")
    buffer = io.StringIO()
    st.session_state.dataframe.info(buf=buffer)
    st.text(buffer.getvalue())
    
    # Display descriptive statistics
    st.subheader("Descriptive Statistics")
    st.write(st.session_state.dataframe.describe())
    
    # Display first few rows
    st.subheader("First 5 Rows")
    st.write(st.session_state.dataframe.head())
    
    # Display missing values
    st.subheader("Missing Values")
    missing_data = st.session_state.dataframe.isnull().sum()
    missing_percent = (missing_data / len(st.session_state.dataframe)) * 100
    missing_df = pd.DataFrame({
        'Missing Values': missing_data,
        'Percentage': missing_percent
    })
    st.write(missing_df)

# Display analysis results
if st.session_state.analysis_results:
    st.header("Analysis Results")
    st.write(st.session_state.analysis_results)
    
    # Display plots
    if st.session_state.plot_files:
        st.header("Generated Plots")
        cols = st.columns(2)
        for i, plot_file in enumerate(st.session_state.plot_files):
            with cols[i % 2]:
                st.image(plot_file, caption=os.path.basename(plot_file))
    else:
        st.info("No plots were generated during the analysis.")
else:
    st.info("Run an analysis to see results here.")

# Footer
st.divider()
st.write("Powered by LangChain and OpenAI")