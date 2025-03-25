@echo off
echo === Data Science Agent Installation ===
echo This script will set up the Data Science Agent.
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set DOCKER_AVAILABLE=true
) else (
    set DOCKER_AVAILABLE=false
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% equ 0 (
    REM Old format (docker-compose) is available
    set DOCKER_COMPOSE_AVAILABLE=true
) else (
    REM Check for new format (docker compose)
    docker compose version >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        set DOCKER_COMPOSE_AVAILABLE=true
    ) else (
        set DOCKER_COMPOSE_AVAILABLE=false
    )
)

REM Always ask user if they want to use Docker
echo Installation options:
echo 1) Install locally (requires Python 3.8+, dependencies will be installed on your system)
echo 2) Run with Docker (recommended, runs in an isolated container)
echo.
set /p INSTALL_METHOD="Do you want to run with Docker instead of installing locally? (y/n) [y]: "

REM Default to Docker if no input
if "%INSTALL_METHOD%"=="" set INSTALL_METHOD=y

REM Accept y/Y as Docker installation
if /i "%INSTALL_METHOD%"=="y" set INSTALL_METHOD=2

if "%INSTALL_METHOD%"=="2" (
    call :install_with_docker
) else (
    call :install_locally
)

goto :eof

:install_with_docker
echo === Installing with Docker ===

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed.
    echo Please install Docker from https://docs.docker.com/get-docker/
    echo.
    echo After installing Docker, run this script again.
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>nul
if %ERRORLEVEL% neq 0 (
    docker compose version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo Error: Docker Compose is not installed.
        echo Please install Docker Compose from https://docs.docker.com/compose/install/
        echo.
        echo After installing Docker Compose, run this script again.
        exit /b 1
    )
)

REM Change to the ds_project directory
cd /d "%~dp0ds_project"

echo Building Docker container (this may take a few minutes)...

REM Build the Docker image
REM Try new format first, then fall back to old format
docker compose version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    docker compose build
) else (
    docker-compose build
)
echo Docker image built successfully! ✓

REM Create necessary directories
if not exist data mkdir data
if not exist eda_plots mkdir eda_plots

echo Docker setup complete!
echo.

REM Prompt user if they want to run the application now
set /p RUN_NOW="Do you want to run the Data Science Agent in Docker now? (y/n) [y]: "

REM Default to yes if no input
if "%RUN_NOW%"=="" set RUN_NOW=y

if /i "%RUN_NOW%"=="y" (
    echo Starting Data Science Agent in Docker...
    call docker-run.bat
) else (
    echo.
    echo To run the Data Science Agent with Docker later:
    echo   docker-run.bat
    echo.
    echo For more information, see DOCKER.md
)
goto :eof

:install_locally
echo === Installing locally ===

REM Run the modified setup script
python setup_modified.py

REM Check if setup was successful
if %ERRORLEVEL% equ 0 (
    echo.
    echo Installation complete!
    echo.
    
    REM Prompt user if they want to run the application now
    set /p RUN_NOW="Do you want to run the Data Science Agent now? (y/n) [y]: "
    
    REM Default to yes if no input
    if "%RUN_NOW%"=="" set RUN_NOW=y
    
    if /i "%RUN_NOW%"=="y" (
        echo Launching the Data Science Agent web interface...
        echo.
        REM Launch the application
        call run.bat
    ) else (
        echo.
        echo To run the Data Science Agent later:
        echo   run.bat
    )
) else (
    echo.
    echo Error: Setup failed with error code %ERRORLEVEL%
    echo Please check the error messages above.
    pause
)
goto :eof