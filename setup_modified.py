#!/usr/bin/env python3
"""
Setup script for the Data Science Agent.
This script installs dependencies and creates the necessary scripts.
It works on Mac, Windows, and Linux.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

# Define the project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DS_PROJECT_DIR = os.path.join(PROJECT_DIR, "ds_project")

def print_step(message):
    """Print a step message with formatting."""
    print(f"\n{'='*80}\n{message}\n{'='*80}")

def run_command(command, shell=False, cwd=None):
    """Run a command and return the output."""
    try:
        if shell:
            process = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, cwd=cwd)
        else:
            process = subprocess.run(command, check=True, text=True, capture_output=True, cwd=cwd)
        return process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Command error: {e.stderr}")
        sys.exit(1)

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_step("Checking Python version")
    
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Error: Python 3.8 or higher is required. You have Python {major}.{minor}.")
        sys.exit(1)
    
    print(f"Python version {major}.{minor} detected. ✓")

def create_virtual_environment():
    """Create a virtual environment using venv."""
    print_step("Creating virtual environment")
    
    venv_dir = os.path.join(DS_PROJECT_DIR, "venv")
    if os.path.exists(venv_dir):
        print(f"Virtual environment already exists at {venv_dir}. ✓")
        return
    
    try:
        import venv
        venv.create(venv_dir, with_pip=True)
        print(f"Virtual environment created at {venv_dir}. ✓")
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)

def install_dependencies():
    """Install dependencies using pip."""
    print_step("Installing dependencies")
    
    # Get the path to the requirements.txt file
    requirements_path = os.path.join(DS_PROJECT_DIR, "requirements.txt")
    
    # Determine the pip executable path based on the platform
    if platform.system() == "Windows":
        pip_path = os.path.join(DS_PROJECT_DIR, "venv", "Scripts", "pip")
    else:
        pip_path = os.path.join(DS_PROJECT_DIR, "venv", "bin", "pip")
    
    # Install dependencies
    try:
        run_command([pip_path, "install", "-r", requirements_path])
        print("Dependencies installed successfully. ✓")
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def create_run_script():
    """Create platform-specific run scripts."""
    print_step("Creating run scripts")
    
    # Create run script for Windows
    with open(os.path.join(DS_PROJECT_DIR, "run.bat"), "w") as f:
        f.write('@echo off\n')
        f.write('echo Starting Data Science Agent...\n')
        f.write('call venv\\Scripts\\activate.bat\n')
        f.write('streamlit run app.py\n')
    
    # Create run script for macOS/Linux
    with open(os.path.join(DS_PROJECT_DIR, "run.sh"), "w") as f:
        f.write('#!/bin/bash\n')
        f.write('echo "Starting Data Science Agent..."\n')
        f.write('source venv/bin/activate\n')
        f.write('streamlit run app.py\n')
    
    # Make the shell script executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(os.path.join(DS_PROJECT_DIR, "run.sh"), 0o755)
    
    print("Run scripts created successfully. ✓")

def create_cli_script():
    """Create platform-specific CLI scripts."""
    print_step("Creating CLI scripts")
    
    # Create CLI script for Windows
    with open(os.path.join(DS_PROJECT_DIR, "analyze.bat"), "w") as f:
        f.write('@echo off\n')
        f.write('call venv\\Scripts\\activate.bat\n')
        f.write('python run_analysis.py %*\n')
    
    # Create CLI script for macOS/Linux
    with open(os.path.join(DS_PROJECT_DIR, "analyze.sh"), "w") as f:
        f.write('#!/bin/bash\n')
        f.write('source venv/bin/activate\n')
        f.write('python run_analysis.py "$@"\n')
    
    # Make the shell script executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(os.path.join(DS_PROJECT_DIR, "analyze.sh"), 0o755)
    
    print("CLI scripts created successfully. ✓")

def create_root_scripts():
    """Create scripts in the root directory that call the scripts in ds_project."""
    print_step("Creating root scripts")
    
    # Create run script for Windows in root directory
    with open(os.path.join(PROJECT_DIR, "run.bat"), "w") as f:
        f.write('@echo off\n')
        f.write('cd /d "%~dp0ds_project"\n')  # Change to ds_project directory
        f.write('call run.bat\n')
    
    # Create run script for macOS/Linux in root directory
    with open(os.path.join(PROJECT_DIR, "run.sh"), "w") as f:
        f.write('#!/bin/bash\n')
        f.write('cd "$(dirname "$0")/ds_project" || exit\n')  # Change to ds_project directory
        f.write('./run.sh\n')
    
    # Make the shell script executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(os.path.join(PROJECT_DIR, "run.sh"), 0o755)
    
    print("Root scripts created successfully. ✓")

def main():
    """Main function to set up the Data Science Agent."""
    print("\nData Science Agent Setup\n")
    
    check_python_version()
    create_virtual_environment()
    install_dependencies()
    create_run_script()
    create_cli_script()
    create_root_scripts()
    
    print_step("Setup completed successfully!")
    
    # Print instructions
    system = platform.system()
    if system == "Windows":
        print("\nTo run the Data Science Agent:")
        print("  - Web interface: run.bat")
        print("  - Command line: ds_project\\analyze.bat --file data/train.csv --objective \"Analyze data\" --api-key YOUR_API_KEY")
    else:
        print("\nTo run the Data Science Agent:")
        print("  - Web interface: ./run.sh")
        print("  - Command line: ./ds_project/analyze.sh --file data/train.csv --objective \"Analyze data\" --api-key YOUR_API_KEY")
    
    print("\nEnjoy using the Data Science Agent!")

if __name__ == "__main__":
    main()