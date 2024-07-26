@echo off
setlocal

:: Get the directory where the batch file is located
set "BASE_DIR=%~dp0"

:: Set the destination folders
set "LAVALINK_DIR=%BASE_DIR%Lavalink"
set "LAVALINK_PLUGINS_DIR=%BASE_DIR%Lavalink\plugins"

:: Set URLs for the Java files
set "LAVALINK_URL=https://github.com/lavalink-devs/Lavalink/releases/download/4.0.7/Lavalink.jar"
set "LAVALINK_PLUGIN_URL1=https://github.com/topi314/LavaSrc/releases/download/4.2.0/lavasrc-plugin-4.2.0.jar"
set "LAVALINK_PLUGIN_URL2=https://github.com/lavalink-devs/youtube-source/releases/download/1.5.0/youtube-plugin-1.5.0.jar"

:: Define paths for files
set "LAVALINK_FILE=%LAVALINK_DIR%\Lavalink.jar"
set "LAVALINK_PLUGIN_FILE1=%LAVALINK_PLUGINS_DIR%\lavasrc-plugin-4.2.0.jar"
set "LAVALINK_PLUGIN_FILE2=%LAVALINK_PLUGINS_DIR%\youtube-plugin-1.5.0.jar"

:: Check if Lavalink.jar exists
if not exist "%LAVALINK_FILE%" (
    echo Downloading Lavalink.jar...
    powershell -Command "Invoke-WebRequest -Uri '%LAVALINK_URL%' -OutFile '%LAVALINK_FILE%'"
) else (
    echo Lavalink.jar already exists. Skipping download.
)

:: Check if lavasrc-plugin-4.2.0.jar exists
if not exist "%LAVALINK_PLUGIN_FILE1%" (
    echo Downloading lavasrc-plugin-4.2.0.jar...
    powershell -Command "Invoke-WebRequest -Uri '%LAVALINK_PLUGIN_URL1%' -OutFile '%LAVALINK_PLUGIN_FILE1%'"
) else (
    echo lavasrc-plugin-4.2.0.jar already exists. Skipping download.
)

:: Check if youtube-plugin-1.5.0.jar exists
if not exist "%LAVALINK_PLUGIN_FILE2%" (
    echo Downloading youtube-plugin-1.5.0.jar...
    powershell -Command "Invoke-WebRequest -Uri '%LAVALINK_PLUGIN_URL2%' -OutFile '%LAVALINK_PLUGIN_FILE2%'"
) else (
    echo youtube-plugin-1.5.0.jar already exists. Skipping download.
)

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

:: Wait for 2 seconds just in case
timeout /t 2 /nobreak >nul

:: Start Lavalink server in a new command prompt window
start "" cmd /c "cd /d %LAVALINK_DIR% && java -jar Lavalink.jar"

echo All processes started!

:: Wait for 5 seconds before closing the main Command Prompt window
timeout /t 1 /nobreak >nul

:: Exit the main Command Prompt window
exit

endlocal
