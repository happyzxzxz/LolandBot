#!/bin/bash

# Set base directory to the location of this script
BASE_DIR="$(dirname "$(realpath "$0")")"

# Virtual environment setup
VENV_DIR="$BASE_DIR/venv"
ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"

if [ ! -f "$ACTIVATE_SCRIPT" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv "$VENV_DIR"
    source "$ACTIVATE_SCRIPT"
    pip install -r "$BASE_DIR/requirements.txt"
else
    echo "Virtual environment already exists. Skipping setup."
    source "$ACTIVATE_SCRIPT"
fi

echo "Setup complete!"

# Start Python bot
echo "Starting Python bot..."
nohup python3 "$BASE_DIR/main.py" > "$BASE_DIR/logs/BotLog.log" 2>&1 &

# Short pause to ensure bot starts
sleep 2

echo "All processes started!"
echo "Check the log files in $BASE_DIR/logs/ for output."

# Final pause to ensure script doesn't close too early
sleep 5
