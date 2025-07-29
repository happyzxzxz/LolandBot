@echo off
setlocal EnableDelayedExpansion

:: Get the directory where the batch file is located
set "BASE_DIR=%~dp0"

:: Remove trailing backslash if present
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

:: Set destination folders
set "LAVALINK_DIR=%BASE_DIR%\Lavalink"
set "LAVALINK_PLUGINS_DIR=%LAVALINK_DIR%\plugins"
set "LOGS_DIR=%BASE_DIR%\logs"
set "LAVALINK_LOGS_DIR=%LAVALINK_DIR%\logs"

:: Define versions for Lavalink and plugins. Use "latest" for the latest version
set "LAVALINK_VERSION=latest"
set "LAVASRC_PLUGIN_VERSION=latest"
set "YOUTUBE_PLUGIN_VERSION=latest"

:: Jump to main script to avoid executing functions prematurely
goto :main

:: Function to get actual version from GitHub API
:GetActualVersion

set "REPO=%~1"

set "URL=https://api.github.com/repos/%REPO%/releases/latest"

set "TEMP_FILE=%TEMP%\github_release_%RANDOM%.json"

:: GitHub API
curl -s -L "%URL%" -o "%TEMP_FILE%"
if errorlevel 1 (
    echo Failed to fetch latest version for %REPO%
    if exist "%TEMP_FILE%" del "%TEMP_FILE%"
    endlocal & set "ACTUAL_VERSION="
    exit /b 1
)

:: PowerShell
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "try { $json = Get-Content '%TEMP_FILE%' -Raw -ErrorAction Stop | ConvertFrom-Json; if ($json.tag_name) { $json.tag_name } else { exit 1 } } catch { exit 1 }"`) do (
    set "VERSION=%%a"
)

if exist "%TEMP_FILE%" del "%TEMP_FILE%"

exit /b 0

:: Function to download a file using curl
:DownloadFile
setlocal
set "URL=%~1"
set "FILE=%~2"

if exist "%FILE%" (
    echo %~nx2 already exists. Skipping download.
    endlocal
    exit /b 0
)

echo Downloading %~nx2...
curl -L -o "%FILE%" "%URL%"
if errorlevel 1 (
    echo Failed to download %~nx2
    del "%FILE%" 2>nul
    endlocal
    exit /b 1
)
:: Verify if the file is a valid JAR (basic check for ZIP header)
for /f "tokens=1-2" %%a in ('powershell -Command "(Get-Content -Path '%FILE%' -Encoding Byte -TotalCount 2 | ForEach-Object { '{0:X2}' -f $_ })"') do (
    set "HEADER=%%a%%b"
)

echo Successfully downloaded %~nx2
endlocal
exit /b

:main
setlocal EnableDelayedExpansion

:: Get actual versions for "latest"
if "%LAVALINK_VERSION%"=="latest" (
    call :GetActualVersion "lavalink-devs/Lavalink"
    set "ACTUAL_LAVALINK_VERSION=!VERSION!"
) else (
    set "ACTUAL_LAVALINK_VERSION=%LAVALINK_VERSION%"
)

if "%LAVASRC_PLUGIN_VERSION%"=="latest" (
    call :GetActualVersion "topi314/LavaSrc"
    set "ACTUAL_LAVASRC_VERSION=!VERSION!"
) else (
    set "ACTUAL_LAVASRC_VERSION=%LAVASRC_PLUGIN_VERSION%"
)

if "%YOUTUBE_PLUGIN_VERSION%"=="latest" (
    call :GetActualVersion "lavalink-devs/youtube-source"
    set "ACTUAL_YOUTUBE_VERSION=!VERSION!"
) else (
    set "ACTUAL_YOUTUBE_VERSION=%YOUTUBE_PLUGIN_VERSION%"
)


:: Set URLs for the Java files
set "LAVALINK_URL=https://github.com/lavalink-devs/Lavalink/releases/download/%ACTUAL_LAVALINK_VERSION%/Lavalink.jar"
set "LAVASRC_PLUGIN_URL=https://github.com/topi314/LavaSrc/releases/download/%ACTUAL_LAVASRC_VERSION%/lavasrc-plugin-%ACTUAL_LAVASRC_VERSION%.jar"
set "YOUTUBE_PLUGIN_URL=https://github.com/lavalink-devs/youtube-source/releases/download/%ACTUAL_YOUTUBE_VERSION%/youtube-plugin-%ACTUAL_YOUTUBE_VERSION%.jar"

:: Define paths for files
set "LAVALINK_FILE=%LAVALINK_DIR%\Lavalink.jar"
set "LAVASRC_PLUGIN_FILE=%LAVALINK_PLUGINS_DIR%\lavasrc-plugin-%ACTUAL_LAVASRC_VERSION%.jar"
set "YOUTUBE_PLUGIN_FILE=%LAVALINK_PLUGINS_DIR%\youtube-plugin-%ACTUAL_YOUTUBE_VERSION%.jar"

:: Create directories if they don't exist
if not exist "%LAVALINK_DIR%" mkdir "%LAVALINK_DIR%"
if not exist "%LAVALINK_PLUGINS_DIR%" mkdir "%LAVALINK_PLUGINS_DIR%"
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"
if not exist "%LAVALINK_LOGS_DIR%" mkdir "%LAVALINK_LOGS_DIR%"

:: Download Lavalink and plugins
call :DownloadFile "%LAVALINK_URL%" "%LAVALINK_FILE%"
if errorlevel 1 exit /b 1
call :DownloadFile "%LAVASRC_PLUGIN_URL%" "%LAVASRC_PLUGIN_FILE%"
if errorlevel 1 exit /b 1
call :DownloadFile "%YOUTUBE_PLUGIN_URL%" "%YOUTUBE_PLUGIN_FILE%"
if errorlevel 1 exit /b 1

:: Check if virtual environment exists
if not exist "%BASE_DIR%\venv\Scripts\activate.bat" (
    echo Setting up the virtual environment...
    python -m venv "%BASE_DIR%\venv"
    call "%BASE_DIR%\venv\Scripts\activate.bat"
    pip install -r "%BASE_DIR%\requirements.txt"
) else (
    echo Virtual environment already exists. Skipping setup.
    call "%BASE_DIR%\venv\Scripts\activate.bat"
)

echo Setup complete!

:: Start the Python bot in a new command prompt window with logging
echo Starting Python bot...
start "" cmd /c "cd /d %BASE_DIR% && python main.py"

:: Wait for 2 seconds to ensure the bot starts
timeout /t 2 /nobreak >nul

:: Start Lavalink server in a new command prompt window with logging
echo Starting Lavalink server...
start "" cmd /c "cd /d %LAVALINK_DIR% && java -jar Lavalink.jar"

echo All processes started!
echo Check the log files in %LOGS_DIR% for output.

:: Final pause to ensure script doesn't close too early
timeout /t 5 /nobreak >nul

endlocal    