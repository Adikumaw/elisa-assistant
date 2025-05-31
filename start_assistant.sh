#!/bin/bash

# Get the directory of the script itself
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/venv" # Assuming venv is in project root

RASA_SERVER_PID=""
RASA_ACTIONS_PID=""
HTTP_SERVER_PID=""

cleanup() {
    echo ""
    echo "Caught signal, cleaning up background processes..."
    # ... (kill commands from previous answer using PIDs) ...
    if [ -n "$HTTP_SERVER_PID" ]; then kill $HTTP_SERVER_PID 2>/dev/null; wait $HTTP_SERVER_PID 2>/dev/null; fi
    if [ -n "$RASA_ACTIONS_PID" ]; then kill $RASA_ACTIONS_PID 2>/dev/null; wait $RASA_ACTIONS_PID 2>/dev/null; fi
    if [ -n "$RASA_SERVER_PID" ]; then kill $RASA_SERVER_PID 2>/dev/null; wait $RASA_SERVER_PID 2>/dev/null; fi
    echo "Cleanup complete."
    exit 0
}
trap cleanup SIGINT SIGTERM

# --- Activate Virtual Environment for Linux/macOS ---
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "Activating Python virtual environment (Linux/macOS)..."
    source "$VENV_DIR/bin/activate"
    VENV_PYTHON="$VENV_DIR/bin/python"
    VENV_RASA="$VENV_DIR/bin/rasa"
    if ! command -v python &> /dev/null || ! command -v rasa &> /dev/null; then
        echo "ERROR: Python or Rasa not found in venv PATH after activation."
        exit 1
    fi
else
    echo "ERROR: Linux/macOS virtual environment not found at $VENV_DIR/bin/activate"
    exit 1
fi

mkdir -p "$SCRIPT_DIR/logs"

echo "Starting Rasa Server (Linux/macOS)..."
cd "$SCRIPT_DIR/rasa"
"$VENV_RASA" run > "$SCRIPT_DIR/logs/rasa_server.log" 2>&1 &
RASA_SERVER_PID=$!
echo "Rasa Server PID: $RASA_SERVER_PID"
cd "$SCRIPT_DIR"

echo "Starting Rasa Actions Server (Linux/macOS)..."
cd "$SCRIPT_DIR/rasa"
"$VENV_RASA" run actions > "$SCRIPT_DIR/logs/rasa_actions.log" 2>&1 &
RASA_ACTIONS_PID=$!
echo "Rasa Actions Server PID: $RASA_ACTIONS_PID"
cd "$SCRIPT_DIR"

echo "Starting Python HTTP Server for UI (Linux/macOS)..."
"$VENV_PYTHON" -m http.server 35109 --directory ./UI > "$SCRIPT_DIR/logs/http_server.log" 2>&1 &
HTTP_SERVER_PID=$!
echo "HTTP Server PID: $HTTP_SERVER_PID"

echo "Starting Main Python Assistant (core/main.py)..."
"$VENV_PYTHON" core/main.py

cleanup