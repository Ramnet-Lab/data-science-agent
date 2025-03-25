#!/bin/bash
# Installation script for the Data Science Agent
# This script will either install locally or set up and run with Docker

echo "=== Data Science Agent Installation ==="
echo "This script will set up the Data Science Agent."
echo ""

# Function to check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check if Docker Compose is installed
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        # Old format (docker-compose)
        return 0
    elif docker compose version &> /dev/null; then
        # New format (docker compose)
        return 0
    else
        return 1
    fi
}

# Function to install with Docker
install_with_docker() {
    echo "=== Installing with Docker ==="
    
    # Check if Docker is installed
    if ! check_docker; then
        echo "Error: Docker is not installed."
        echo "Please install Docker from https://docs.docker.com/get-docker/"
        echo ""
        echo "After installing Docker, run this script again."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! check_docker_compose; then
        echo "Error: Docker Compose is not installed."
        echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
        echo ""
        echo "After installing Docker Compose, run this script again."
        exit 1
    fi
    
    # Change to the ds_project directory
    cd "$(dirname "$0")/ds_project" || exit
    
    echo "Building Docker container (this may take a few minutes)..."
    
    # Build the Docker image
    # Try new format first, then fall back to old format
    if docker compose version &> /dev/null; then
        docker compose build
    else
        docker-compose build
    fi

    # Make sure docker-run.sh is executable
    chmod +x docker-run.sh
    echo "Docker image built successfully! ✓"

    # Create necessary directories
    mkdir -p data eda_plots

    echo "Docker setup complete!"
    echo ""

    # Prompt user if they want to run the application now
    read -p "Do you want to run the Data Science Agent in Docker now? (y/n) [y]: " RUN_NOW
    RUN_NOW=${RUN_NOW:-y}

    if [ "$RUN_NOW" = "y" ] || [ "$RUN_NOW" = "Y" ]; then
        echo "Starting Data Science Agent in Docker..."
        ./docker-run.sh
    else
        echo ""
        echo "To run the Data Science Agent with Docker later:"
        echo "  ./docker-run.sh"
        echo ""
        echo "For more information, see DOCKER.md"
    fi
}

# Function to install locally
install_locally() {
    echo "=== Installing locally ==="

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed or not in your PATH."
        echo "Please install Python 3.8 or higher and try again."
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        echo "Error: Python 3.8 or higher is required. You have Python $PYTHON_VERSION."
        echo "Please upgrade your Python installation and try again."
        exit 1
    fi

    echo "Python $PYTHON_VERSION detected. ✓"
    echo ""

    # Run the modified setup script
    echo "Running setup script..."
    python3 setup_modified.py

    echo ""
    echo "Installation complete!"
    echo ""

    # Prompt user if they want to run the application now
    read -p "Do you want to run the Data Science Agent now? (y/n) [y]: " RUN_NOW
    RUN_NOW=${RUN_NOW:-y}

    if [ "$RUN_NOW" = "y" ] || [ "$RUN_NOW" = "Y" ]; then
        echo "Launching the Data Science Agent web interface..."
        echo ""
        # Launch the application
        ./run.sh
    else
        echo ""
        echo "To run the Data Science Agent later:"
        echo "  ./run.sh"
    fi
}

# Check if Docker is available
DOCKER_AVAILABLE=false
if check_docker && check_docker_compose; then
    DOCKER_AVAILABLE=true
fi

# Always ask user if they want to use Docker
echo "Installation options:"
echo "1) Install locally (requires Python 3.8+, dependencies will be installed on your system)"
echo "2) Run with Docker (recommended, runs in an isolated container)"
echo ""
read -p "Do you want to run with Docker instead of installing locally? (y/n) [y]: " INSTALL_METHOD
INSTALL_METHOD=${INSTALL_METHOD:-y}

if [ "$INSTALL_METHOD" = "y" ] || [ "$INSTALL_METHOD" = "Y" ] || [ "$INSTALL_METHOD" = "2" ]; then
    install_with_docker
else
    install_locally
fi