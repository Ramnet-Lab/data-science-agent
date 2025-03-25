#!/usr/bin/env python3
"""
Setup script for the Data Science Agent.
This script installs UV and uses it to install all dependencies.
It works on Mac, Windows, and Linux.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def print_step(message):
    """Print a step message with formatting."""
    print(f"\n{'='*80}\n{message}\n{'='*80}")

def run_command(command, shell=False):
    """Run a command and return the output."""
    try:
        if shell:
            process = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        else:
            process = subprocess.run(command, check=True, text=True, capture_output=True)
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

def install_uv():
    """Install UV if not already installed."""
    print_step("Installing UV package installer")
    
    # Check if UV is already installed
    uv_path = shutil.which("uv")
    if uv_path:
        print(f"UV is already installed at {uv_path}. ✓")
        return
    
    # Install UV based on the platform
    system = platform.system().lower()
    
    try:
        if system == "windows":
            # For Windows
            run_command(["curl", "-sSf", "https://astral.sh/uv/install.ps1", "-o", "install.ps1"])
            run_command(["powershell", "-ExecutionPolicy", "Bypass", "-File", "install.ps1"])
            # Clean up
            if os.path.exists("install.ps1"):
                os.remove("install.ps1")
        else:
            # For macOS and Linux
            run_command("curl -sSf https://astral.sh/uv/install.sh | sh", shell=True)
        
        # Verify installation
        uv_path = shutil.which("uv")
        if not uv_path:
            # Try to find UV in the user's home directory
            home_dir = Path.home()
            possible_paths = [
                home_dir / ".cargo" / "bin" / "uv",
                home_dir / ".uv" / "bin" / "uv"
            ]
            
            for path in possible_paths:
                if path.exists():
                    os.environ["PATH"] = f"{path.parent}:{os.environ['PATH']}"
                    print(f"Added {path.parent} to PATH")
                    break
            
            uv_path = shutil.which("uv")
            if not uv_path:
                print("Error: UV installation failed. Please install manually from https://github.com/astral-sh/uv")
                sys.exit(1)
        
        print(f"UV installed successfully at {uv_path}. ✓")
    
    except Exception as e:
        print(f"Error installing UV: {e}")
        print("Please install UV manually from https://github.com/astral-sh/uv")
        sys.exit(1)

def create_virtual_environment():
    """Create a virtual environment using UV."""
    print_step("Creating virtual environment")
    
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print(f"Virtual environment already exists at {venv_dir}. ✓")
        return
    
    run_command(["uv", "venv", venv_dir])
    print(f"Virtual environment created at {venv_dir}. ✓")

def install_dependencies():
    """Install dependencies using UV."""
    print_step("Installing dependencies")
    
    # Get the path to the requirements.txt file
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    # Install dependencies
    run_command(["uv", "pip", "install", "-r", requirements_path])
    print("Dependencies installed successfully. ✓")

def create_run_script():
    """Create platform-specific run scripts."""
    print_step("Creating run scripts")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create run script for Windows
    with open(os.path.join(current_dir, "run.bat"), "w") as f:
        f.write('@echo off\n')
        f.write('echo Starting Data Science Agent...\n')
        f.write('call venv\\Scripts\\activate.bat\n')
        f.write('streamlit run app.py\n')
    
    # Create run script for macOS/Linux
    with open(os.path.join(current_dir, "run.sh"), "w") as f:
        f.write('#!/bin/bash\n')
        f.write('echo "Starting Data Science Agent..."\n')
        f.write('source venv/bin/activate\n')
        f.write('streamlit run app.py\n')
    
    # Make the shell script executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(os.path.join(current_dir, "run.sh"), 0o755)
    
    print("Run scripts created successfully. ✓")

def create_cli_script():
    """Create platform-specific CLI scripts."""
    print_step("Creating CLI scripts")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create CLI script for Windows
    with open(os.path.join(current_dir, "analyze.bat"), "w") as f:
        f.write('@echo off\n')
        f.write('call venv\\Scripts\\activate.bat\n')
        f.write('python run_analysis.py %*\n')
    
    # Create CLI script for macOS/Linux
    with open(os.path.join(current_dir, "analyze.sh"), "w") as f:
        f.write('#!/bin/bash\n')
        f.write('source venv/bin/activate\n')
        f.write('python run_analysis.py "$@"\n')
    
    # Make the shell script executable on Unix-like systems
    if platform.system() != "Windows":
        os.chmod(os.path.join(current_dir, "analyze.sh"), 0o755)
    
    print("CLI scripts created successfully. ✓")

def main():
    """Main function to set up the Data Science Agent."""
    print("\nData Science Agent Setup\n")
    
    check_python_version()
    install_uv()
    create_virtual_environment()
    install_dependencies()
    create_run_script()
    create_cli_script()
    
    print_step("Setup completed successfully!")
    
    # Print instructions
    system = platform.system()
    if system == "Windows":
        print("\nTo run the Data Science Agent:")
        print("  - Web interface: run.bat")
        print("  - Command line: analyze.bat --file data/train.csv --objective \"Analyze data\" --api-key YOUR_API_KEY")
    else:
        print("\nTo run the Data Science Agent:")
        print("  - Web interface: ./run.sh")
        print("  - Command line: ./analyze.sh --file data/train.csv --objective \"Analyze data\" --api-key YOUR_API_KEY")
    
    print("\nEnjoy using the Data Science Agent!")

if __name__ == "__main__":
    main()