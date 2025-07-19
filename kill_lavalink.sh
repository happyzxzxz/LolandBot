#!/bin/bash

# Set base directory to the location of this script
BASE_DIR="$(dirname "$(realpath "$0")")"

# Find the PID of the Lavalink process
LAVALINK_PID=$(pgrep -f "java -jar $BASE_DIR/Lavalink/Lavalink.jar")

# Check if Lavalink is running
if [ -z "$LAVALINK_PID" ]; then
    echo "Lavalink is not running."
else
    echo "Stopping Lavalink (PID: $LAVALINK_PID)..."
    kill "$LAVALINK_PID"

    # Wait for the process to terminate
    sleep 2

    # Verify if the process was killed
    if pgrep -f "java -jar $BASE_DIR/Lavalink/Lavalink.jar" > /dev/null; then
        echo "Failed to stop Lavalink. Trying force kill..."
        kill -9 "$LAVALINK_PID"
    fi
    echo "Lavalink has been stopped."
fi
