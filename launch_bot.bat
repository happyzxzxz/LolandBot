@echo off
setlocal

:: Get the directory where the batch file is located
set "BASE_DIR=%~dp0"

:: Check if virtual environment exists
if not exist "%BASE_DIR%venv\Scripts\activate" (
    echo Setting up the virtual environment...
    python -m venv venv

    :: Activate the virtual environment and install dependencies
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
    echo Virtual environment already exists. Skipping setup.
)

echo Setup complete!

:: Start the Python bot in a new command prompt window
start "" cmd /k "python "%BASE_DIR%main.py" || pause"