#!/bin/bash

# Set base directory to the location of this script
BASE_DIR="$(dirname "$(realpath "$0")")"

# Set destination folders
LAVALINK_DIR="$BASE_DIR/Lavalink"
LAVALINK_PLUGINS_DIR="$LAVALINK_DIR/plugins"

# Define versions for Lavalink and plugins. "latest" for the latest or just the version (like 1.12.2)
LAVALINK_VERSION="latest"
LAVASRC_PLUGIN_VERSION="latest"
YOUTUBE_PLUGIN_VERSION="latest"

# Fetch actual version for Lavalink and plugins. DO NOT TOUCH THIS

get_actual_version() {
    local url="$1"

    if [[ $(basename "$url") == "latest" ]]; then
        FINAL_URL=$(wget --max-redirect=10 --spider "$url" 2>&1 | grep -i Location | tail -n 1 | awk '{print $2}')
        VERSION=$(basename "$FINAL_URL")

        echo "$VERSION"
    else
        echo $(basename "$url")
    fi
}

ACTUAL_LAVALINK_VERSION=$(get_actual_version "https://github.com/lavalink-devs/Lavalink/releases/${LAVALINK_VERSION}")
ACTUAL_LAVASRC_VERSION=$(get_actual_version "https://github.com/topi314/LavaSrc/releases/${LAVASRC_PLUGIN_VERSION}")
ACTUAL_YOUTUBE_VERSION=$(get_actual_version "https://github.com/lavalink-devs/youtube-source/releases/${YOUTUBE_PLUGIN_VERSION}")

# Set URLs for the Java files
LAVALINK_URL="https://github.com/lavalink-devs/Lavalink/releases/download/${ACTUAL_LAVALINK_VERSION}/Lavalink.jar"
LAVASRC_PLUGIN_URL="https://github.com/topi314/LavaSrc/releases/download/${ACTUAL_LAVASRC_VERSION}/lavasrc-plugin-${ACTUAL_LAVASRC_VERSION}.jar"
YOUTUBE_PLUGIN_URL="https://github.com/lavalink-devs/youtube-source/releases/download/${ACTUAL_YOUTUBE_VERSION}/youtube-plugin-${ACTUAL_YOUTUBE_VERSION}.jar"

# Define paths for files
LAVALINK_FILE="$LAVALINK_DIR/Lavalink.jar"
LAVASRC_PLUGIN_FILE="$LAVALINK_PLUGINS_DIR/lavasrc-plugin-${ACTUAL_LAVASRC_VERSION}.jar"
YOUTUBE_PLUGIN_FILE="$LAVALINK_PLUGINS_DIR/youtube-plugin-${ACTUAL_YOUTUBE_VERSION}.jar"

# Create required directories
mkdir -p "$LAVALINK_DIR"
mkdir -p "$LAVALINK_PLUGINS_DIR"
mkdir -p "$LAVALINK_DIR/logs"

# Download function
download_file() {
    local url="$1"
    local file="$2"

    if [ ! -f "$file" ]; then
        echo "Downloading $(basename "$file")..."
        if ! wget -O "$file" "$url"; then
            echo "Failed to download $(basename "$file")"
            exit 1
        fi
    else
        echo "$(basename "$file") already exists. Skipping download."
    fi
}

# Download Lavalink and plugins
download_file "$LAVALINK_URL" "$LAVALINK_FILE"
download_file "$LAVASRC_PLUGIN_URL" "$LAVASRC_PLUGIN_FILE"
download_file "$YOUTUBE_PLUGIN_URL" "$YOUTUBE_PLUGIN_FILE"

# Start Lavalink server
echo "Starting Lavalink server..."
cd "$LAVALINK_DIR" || exit
nohup java -jar "$LAVALINK_FILE" > "$LAVALINK_DIR/logs/spring.log" 2>&1 &

# Final pause to ensure script doesn't close too early
sleep 5
