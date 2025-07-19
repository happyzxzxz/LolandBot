@echo off
setlocal EnableDelayedExpansion

:: Get the directory where the batch file is located
set "BASE_DIR=%~dp0"

:: Remove trailing backslash if present
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

:: Set destination folders
set "LAVALINK_DIR=%BASE_DIR%\Lavalink"
set "LAVALINK_PLUGINS_DIR=%LAVALINK_DIR%\plugins"
set "LAVALINK_LOGS_DIR=%LAVALINK_DIR%\logs"

:: Define versions for Lavalink and plugins. Use "latest" for the latest version
set "LAVALINK_VERSION=latest"
set "LAVASRC_PLUGIN_VERSION=latest"
set "YOUTUBE_PLUGIN_VERSION=latest"

:: Jump to main script to avoid executing functions prematurely
goto :main

:: Function to get actual version from GitHub release URL
:GetActualVersion
setlocal
set "URL=%~1"
:: Extract the basename of the URL
for %%a in ("%URL%") do set "BASENAME=%%~nxa"
if /i "!BASENAME!"=="latest" (
    set "TEMP_FILE=%TEMP%\github_redirect_%RANDOM%.txt"
    curl -s -I -L --max-redirs 10 "%URL%" > "!TEMP_FILE!"
    for /f "tokens=2" %%a in ('findstr /i "location:" "!TEMP_FILE!"') do set "FINAL_URL=%%a"
    for %%a in (!FINAL_URL!) do set "VERSION=%%~nxa"
    del "!TEMP_FILE!"
) else (
    set "VERSION=!BASENAME!"
)
endlocal & set "ACTUAL_VERSION=%VERSION%"
exit /b

:: Function to download a file if it doesn't exist using curl
:DownloadFile
setlocal
set "URL=%~1"
set "FILE=%~2"
if not exist "%FILE%" (
    echo Downloading %~nx2...
    curl -L -o "%FILE%" "%URL%"
    if errorlevel 1 (
        echo Failed to download %~nx2
        exit /b 1
    )
) else (
    echo %~nx2 already exists. Skipping download.
)
endlocal
exit /b

:main
:: Get actual versions for "latest"
if "%LAVALINK_VERSION%"=="latest" (
    call :GetActualVersion "https://github.com/lavalink-devs/Lavalink/releases/latest"
    set "ACTUAL_LAVALINK_VERSION=%ACTUAL_VERSION%"
) else (
    set "ACTUAL_LAVALINK_VERSION=%LAVALINK_VERSION%"
)

if "%LAVASRC_PLUGIN_VERSION%"=="latest" (
    call :GetActualVersion "https://github.com/topi314/LavaSrc/releases/latest"
    set "ACTUAL_LAVASRC_VERSION=%ACTUAL_VERSION%"
) else (
    set "ACTUAL_LAVASRC_VERSION=%LAVASRC_PLUGIN_VERSION%"
)

if "%YOUTUBE_PLUGIN_VERSION%"=="latest" (
    call :GetActualVersion "https://github.com/lavalink-devs/youtube-source/releases/latest"
    set "ACTUAL_YOUTUBE_VERSION=%ACTUAL_VERSION%"
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
if not exist "%LAVALINK_LOGS_DIR%" mkdir "%LAVALINK_LOGS_DIR%"

:: Download Lavalink and plugins
call :DownloadFile "%LAVALINK_URL%" "%LAVALINK_FILE%"
call :DownloadFile "%LAVASRC_PLUGIN_URL%" "%LAVASRC_PLUGIN_FILE%"
call :DownloadFile "%YOUTUBE_PLUGIN_URL%" "%YOUTUBE_PLUGIN_FILE%"

:: Start Lavalink server in a new command prompt window with logging
echo Starting Lavalink server...
start "" cmd /c "cd /d %LAVALINK_DIR% && java -jar Lavalink.jar > logs\spring.log 2>&1"

echo Lavalink server started!
echo Check the log files in %LAVALINK_LOGS_DIR% for output.

:: Final pause to ensure script doesn't close too early
timeout /t 5 /nobreak >nul

endlocal