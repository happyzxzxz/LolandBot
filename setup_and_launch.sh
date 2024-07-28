#!/bin/bash

# Set base directory to the location of this script
BASE_DIR="$(dirname "$(realpath "$0")")"

# Set destination folders
LAVALINK_DIR="$BASE_DIR/Lavalink"
LAVALINK_PLUGINS_DIR="$LAVALINK_DIR/plugins"

# Set URLs for the Java files
LAVALINK_URL="https://github.com/lavalink-devs/Lavalink/releases/download/4.0.7/Lavalink.jar"
LAVALINK_PLUGIN_URL1="https://github.com/topi314/LavaSrc/releases/download/4.2.0/lavasrc-plugin-4.2.0.jar"
LAVALINK_PLUGIN_URL2="https://github.com/lavalink-devs/youtube-source/releases/download/1.5.0/youtube-plugin-1.5.0.jar"

# Define paths for files
LAVALINK_FILE="$LAVALINK_DIR/Lavalink.jar"
LAVALINK_PLUGIN_FILE1="$LAVALINK_PLUGINS_DIR/lavasrc-plugin-4.2.0.jar"
LAVALINK_PLUGIN_FILE2="$LAVALINK_PLUGINS_DIR/youtube-plugin-1.5.0.jar"

# Ensure Lavalink directory exists
mkdir -p "$LAVALINK_DIR"
mkdir -p "$LAVALINK_PLUGINS_DIR"

# Check if Lavalink.jar exists
if [ ! -f "$LAVALINK_FILE" ]; then
    echo "Downloading Lavalink.jar..."
    wget -O "$LAVALINK_FILE" "$LAVALINK_URL"
else
    echo "Lavalink.jar already exists. Skipping download."
fi

# Check if lavasrc-plugin-4.2.0.jar exists
if [ ! -f "$LAVALINK_PLUGIN_FILE1" ]; then
    echo "Downloading lavasrc-plugin-4.2.0.jar..."
    wget -O "$LAVALINK_PLUGIN_FILE1" "$LAVALINK_PLUGIN_URL1"
else
    echo "lavasrc-plugin-4.2.0.jar already exists. Skipping download."
fi

# Check if youtube-plugin-1.5.0.jar exists
if [ ! -f "$LAVALINK_PLUGIN_FILE2" ]; then
    echo "Downloading youtube-plugin-1.5.0.jar..."
    wget -O "$LAVALINK_PLUGIN_FILE2" "$LAVALINK_PLUGIN_URL2"
else
    echo "youtube-plugin-1.5.0.jar already exists. Skipping download."
fi

# Check if virtual environment exists
if [ ! -d "$BASE_DIR/venv" ]; then
    echo "Setting up the virtual environment..."
    python3 -m venv "$BASE_DIR/venv"
    
    # Activate the virtual environment and install dependencies
    source "$BASE_DIR/venv/bin/activate"
    pip install -r "$BASE_DIR/requirements.txt"

else
    echo "Virtual environment already exists. Skipping setup."
    source "$BASE_DIR/venv/bin/activate"
fi

echo "Setup complete!"

# Start the Python bot in the background
echo "Starting Python bot..."
nohup python3 "$BASE_DIR/main.py" > "$BASE_DIR/logs/BotLog.log" 2>&1 &

# Wait for 2 seconds just in case
sleep 2

# Start Lavalink server in the background
echo "Starting Lavalink server..."
cd "$BASE_DIR/Lavalink"
nohup java -jar "$LAVALINK_FILE" > "$BASE_DIR/Lavalink/logs/spring.log" 2>&1 &

echo "All processes started!"

# Wait for 5 seconds before exiting the script
sleep 5

# Script ends here
