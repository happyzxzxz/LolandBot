
#!/bin/bash

# Set base directory to the location of this script
BASE_DIR="$(dirname "$(realpath "$0")")"

# Find the PID of the Lavalink process
BOT_PID=$(pgrep -f "python3 $BASE_DIR/main.py")

# Check if Lavalink is running
if [ -z "$BOT_PID" ]; then
    echo "Bot is not running."
else
    echo "Stopping Bot (PID: $BOT_PID)..."
    kill "$BOT_PID"

    # Wait for the process to terminate
    sleep 2

    # Verify if the process was killed
    if pgrep -f "python3 $BASE_DIR/main.py" > /dev/null; then
        echo "Failed to stop Bot. Trying force kill..."
        kill -9 "$BOT_PID"
    fi
    echo "Bot has been stopped."
fi
