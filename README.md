# Data Science Agent

![Data Science Agent](ds_project/project%20image/DALL·E%202025-03-24%2017.47.04%20-%20A%20master%20data%20scientist%20sits%20at%20a%20large%20oak%20desk%20in%20a%20dimly%20lit%2C%20cathedral-like%20library%20filled%20with%20ancient%20books%2C%20glowing%20monitors%2C%20and%20old%20computing.webp)

This project converts a Jupyter notebook-based data science agent into a Python application with a Streamlit interface. The agent uses LangChain and OpenAI to generate and execute data analysis code.

## Features

- Upload CSV or Excel files for analysis
- Configure analysis objectives and hardware specifications
- Generate optimized Python code for data analysis
- Run in Docker with automatic container management
- Configure maximum iterations for analysis
- Focus on data analysis results without code explanations
- Execute the generated code and display results
- Visualize data with automatically generated plots

## Project Structure

```
ds_project/
├── app.py                  # Streamlit application
├── docker-compose.yml      # Docker Compose configuration
├── DOCKER.md               # Docker setup instructions
├── Dockerfile              # Docker configuration
├── requirements.txt        # Project dependencies
├── setup.py                # Setup script for easy installation
├── run_analysis.py         # Command-line interface
├── analyze.sh              # Analysis script for macOS/Linux
├── analyze.bat             # Analysis script for Windows
├── docker-run.sh           # Docker run script for macOS/Linux
├── docker-run.bat          # Docker run script for Windows
├── run.sh                  # Run script for macOS/Linux
├── run.bat                 # Run script for Windows
├── data/                   # Directory for data files
├── eda_plots/              # Directory for generated plots
├── src/                    # Source code
│   ├── __init__.py
│   ├── agent.py            # Data Science Agent implementation
│   ├── models.py           # Pydantic models
│   └── tools.py            # Agent tools
├── .dockerignore           # Docker ignore file
└── .gitignore              # Git ignore file
```

## Quick Setup (Recommended)

The easiest way to set up the Data Science Agent is to use the provided installation scripts, which work on Mac, Windows, and Linux:

### On macOS/Linux:

```bash
# Run the installation script
./install.sh
```

### On Windows:

```
# Run the installation script
install.bat
```

These scripts will:
1. Check your Python version (requires Python 3.8+)
2. Install UV (a fast Python package installer)
3. Create a virtual environment
4. Install all dependencies using UV
5. Create platform-specific run scripts
6. Automatically launch the application

The application will start automatically after installation is complete. In the future, you can run the application using:
- On Windows: `run.bat`
- On macOS/Linux: `./run.sh`

### Manual Setup with setup.py

You can also run the setup script directly:

```bash
# Run the setup script
python setup.py
```

## Manual Setup (Alternative)

If you prefer to set up manually:

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   
   Or with UV (faster):
   ```
   uv pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Docker Setup

The Data Science Agent can also be run using Docker, which provides an isolated environment with all dependencies pre-installed.

### Quick Start with Docker

1. Use the provided scripts to run the application in Docker:

   - On macOS/Linux:
     ```bash
     ./docker-run.sh
     ```

   - On Windows:
     ```
     docker-run.bat
     ```

2. Access the application in your browser at [http://localhost:8502](http://localhost:8502)

### Manual Docker Setup

Alternatively, you can use Docker Compose directly:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your_openai_api_key_here

# Start the application
docker-compose up
```

For more detailed instructions on using Docker, see the [DOCKER.md](ds_project/DOCKER.md) file.

## Usage

1. Enter your OpenAI API key in the sidebar
2. Initialize the agent
3. Upload a data file or provide a file path
4. Configure analysis objectives and hardware specifications
5. Run the analysis
6. View the results and generated plots

### Advanced Configuration

The Data Science Agent includes several advanced configuration options:

- **Max Iterations**: Control the maximum number of iterations the agent can perform. Increase this value if the agent is stopping before completing the analysis.
- **Model Selection**: Choose from available OpenAI models based on your API key.
- **Analysis Objective**: Customize the analysis objective to focus on specific aspects of your data.
- **Hardware Specifications**: Provide information about your hardware to optimize the generated code.

## How It Works

The Data Science Agent uses a combination of LangChain, OpenAI's GPT models, and custom tools to:

1. **Read and analyze data files** - The agent examines the structure, data types, and content of uploaded CSV or Excel files
2. **Generate optimized Python code** - Based on the analysis objectives and hardware specifications, the agent creates custom data analysis code
3. **Execute the generated code** - The code is executed in a controlled environment, with results and visualizations captured
4. **Provide comprehensive analysis** - Results include an analysis summary, key insights, and recommendations

The agent follows a structured workflow:
- Data ingestion and preprocessing
- Exploratory data analysis
- Visualization generation
- Insight extraction

## Command-Line Interface

In addition to the Streamlit web interface, the project includes a command-line tool for batch processing:

### Using the CLI Scripts (Recommended)

If you used the setup script, you can use the provided CLI scripts:

- On Windows:
  ```
  analyze.bat --file data/train.csv --objective "Analyze survival patterns" --api-key YOUR_API_KEY
  ```

- On macOS/Linux:
  ```
  ./analyze.sh --file data/train.csv --objective "Analyze survival patterns" --api-key YOUR_API_KEY
  ```

### Manual CLI Usage

Alternatively, you can run the analysis script directly:

```bash
python run_analysis.py --file data/train.csv --objective "Analyze survival patterns" --api-key YOUR_API_KEY
```

## Technologies Used

- **LangChain** - Framework for developing applications powered by language models
- **OpenAI GPT Models** - Advanced language models for code generation and analysis
- **Streamlit** - Web application framework for data applications
- **Pandas & NumPy** - Data manipulation and analysis
- **Matplotlib & Seaborn** - Data visualization
- **Scikit-learn** - Machine learning tools
- **Docker** - Containerization for consistent environments
 
## Requirements

- Python 3.8+
- OpenAI API key
- Dependencies listed in requirements.txt (automatically installed by the setup script)

The setup script will automatically install UV (a fast Python package installer) and use it to install all dependencies.

## Example Analyses

The Data Science Agent can perform various types of analyses, including:

- Exploratory data analysis with automatic visualization
- Feature correlation and importance analysis
- Pattern and trend identification
- Statistical hypothesis testing
- Basic predictive modeling

## Recent Updates

- **Simplified Directory Structure**: Consolidated scripts by moving them from platform-specific directories (unix/ and win/) to the project root for easier access
- **Docker Support**: Added Docker configuration for easy deployment and consistent environments
- **Iteration Configuration**: Added ability to configure maximum iterations for analysis
- **Focus on Data Analysis**: Updated AI prompts to focus on data analysis results without code explanations
- **Container Management**: Added automatic container cleanup to prevent conflicts
- **Performance Improvements**: Removed multiprocessing suggestions to avoid execution errors
- **Project Cleanup**: Removed unnecessary files and updated .gitignore
- **Original Jupyter Notebook**: Included the original DataSci_Agent.ipynb notebook for reference

## Disclaimer

**IMPORTANT: Please read this disclaimer carefully before using the Data Science Agent.**

This application is capable of generating and executing code for data analysis, including resource-intensive operations such as machine learning, linear regression, and other computational tasks. When prompted to perform such operations on large datasets, the application will attempt to execute them using the available system resources.

### Potential Risks:

- **System Performance**: Executing resource-intensive operations on large datasets may cause your system to become unresponsive or slow.
- **Hardware Stress**: Prolonged execution of computationally intensive tasks may cause excessive CPU/GPU usage, leading to overheating or increased wear on hardware components.
- **Memory Usage**: Large datasets may consume significant amounts of RAM, potentially causing system instability.
- **Storage Impact**: Generated files and intermediate data may consume substantial disk space.

### Liability Disclaimer:

The creator and contributors of this software are not liable for any damage, data loss, or hardware issues that may result from using this application. By using this software, you acknowledge that:

1. You understand the potential risks associated with executing AI-generated code on your system.
2. You accept full responsibility for monitoring system resources during execution.
3. You will use appropriate caution when processing large datasets or requesting resource-intensive analyses.
4. You will implement proper safeguards (such as setting resource limits or using dedicated environments) when necessary.

It is recommended to test the application with small datasets first and gradually increase the size as you become familiar with its performance characteristics on your specific hardware.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.