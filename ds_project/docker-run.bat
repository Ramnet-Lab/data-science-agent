@echo off
REM Script to run the Data Science Agent in Docker on Windows

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed. Please install Docker first.
    echo Visit https://docs.docker.com/get-docker/ for installation instructions.
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    REM Check for new format (docker compose)
    docker compose version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Error: Docker Compose is not installed. Please install Docker Compose first.
        echo Visit https://docs.docker.com/compose/install/ for installation instructions.
        exit /b 1
    )
)

REM Create necessary directories if they don't exist
if not exist data mkdir data
if not exist eda_plots mkdir eda_plots

REM Check if the container already exists and remove it
docker ps -a | findstr "data-science-agent" >nul
if %ERRORLEVEL% equ 0 (
    echo Found existing data-science-agent container. Stopping and removing it...
    docker stop data-science-agent >nul 2>&1
    docker rm data-science-agent >nul 2>&1
    echo Old container removed.
)

REM Check if the Docker image exists
docker images | findstr "ds_project_data-science-agent" >nul
if %ERRORLEVEL% neq 0 (
    echo Docker image not found. Building image...
    REM Try new format first, then fall back to old format
    docker compose version >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        docker compose build
    ) else (
        docker-compose build
    )
)

REM Build and run the Docker container
echo Starting Data Science Agent in Docker on http://localhost:8502 ...
echo Press Ctrl+C to stop the container.
echo Note: You will need to enter your OpenAI API key in the web interface.

REM Try new format first, then fall back to old format
docker compose version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    docker compose up
) else (
    docker-compose up
)