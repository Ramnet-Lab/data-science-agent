#!/bin/bash
# Script to run the Data Science Agent in Docker

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    # Check for new format (docker compose)
    if ! docker compose version &> /dev/null; then
        echo "Error: Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit https://docs.docker.com/compose/install/ for installation instructions."
        exit 1
    fi
fi

# Create necessary directories if they don't exist
mkdir -p data eda_plots

# Check if the container already exists and remove it
if docker ps -a | grep -q "data-science-agent"; then
    echo "Found existing data-science-agent container. Stopping and removing it..."
    docker stop data-science-agent >/dev/null 2>&1
    docker rm data-science-agent >/dev/null 2>&1
    echo "Old container removed."
fi

# Check if the Docker image exists
if ! docker images | grep -q "ds_project_data-science-agent"; then
    echo "Docker image not found. Building image..."
    # Try new format first, then fall back to old format
    if docker compose version &> /dev/null; then
        docker compose build
    else
        docker-compose build
    fi
fi

# Run the Docker container
echo "Starting Data Science Agent in Docker on http://localhost:8502 ..."
echo "Press Ctrl+C to stop the container."
echo "Note: You will need to enter your OpenAI API key in the web interface."

# Try new format first, then fall back to old format
if docker compose version &> /dev/null; then
    docker compose up
else
    docker-compose up
fi