#!/bin/bash

# Get the directory of the script itself
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# --- Store PIDs of background processes ---
RASA_SERVER_PID=""
RASA_ACTIONS_PID=""
HTTP_SERVER_PID=""
MAIN_PYTHON_PID="" # PID of core/main.py if we run it in background too

# --- Cleanup function ---
cleanup() {
    echo "" # Newline after ^C
    echo "Caught signal, cleaning up background processes..."

    if [ -n "$MAIN_PYTHON_PID" ]; then
        echo "Stopping Main Python Assistant (PID $MAIN_PYTHON_PID)..."
        kill $MAIN_PYTHON_PID 2>/dev/null
        wait $MAIN_PYTHON_PID 2>/dev/null # Wait for it to actually exit
    fi
    if [ -n "$HTTP_SERVER_PID" ]; then
        echo "Stopping HTTP Server (PID $HTTP_SERVER_PID)..."
        kill $HTTP_SERVER_PID 2>/dev/null
        wait $HTTP_SERVER_PID 2>/dev/null
    fi
    if [ -n "$RASA_ACTIONS_PID" ]; then
        echo "Stopping Rasa Actions Server (PID $RASA_ACTIONS_PID)..."
        kill $RASA_ACTIONS_PID 2>/dev/null
        wait $RASA_ACTIONS_PID 2>/dev/null
    fi
    if [ -n "$RASA_SERVER_PID" ]; then
        echo "Stopping Rasa Server (PID $RASA_SERVER_PID)..."
        kill $RASA_SERVER_PID 2>/dev/null
        wait $RASA_SERVER_PID 2>/dev/null
    fi

    # Deactivate venv if active (optional, as shell exits)
    # if type deactivate > /dev/null 2>&1; then
    #     echo "Deactivating virtual environment..."
    #     deactivate
    # fi
    echo "Cleanup complete."
    exit 0 # Exit the script cleanly
}

# Trap SIGINT (Ctrl+C) and SIGTERM (kill command)
trap cleanup SIGINT SIGTERM

# --- Activate Virtual Environment ---
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    echo "Activating Python virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "ERROR: Virtual environment not found at $SCRIPT_DIR/venv/bin/activate"
    exit 1
fi
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"
VENV_RASA="$SCRIPT_DIR/venv/bin/rasa"

mkdir -p "$SCRIPT_DIR/logs"

echo "Starting Rasa Server..."
cd "$SCRIPT_DIR/rasa"
# Using $VENV_RASA. Output to logs. Run in background.
"$VENV_RASA" run > "$SCRIPT_DIR/logs/rasa_server.log" 2>&1 &
RASA_SERVER_PID=$!
echo "Rasa Server started with PID $RASA_SERVER_PID. Log: logs/rasa_server.log"
cd "$SCRIPT_DIR"

echo "Starting Rasa Actions Server..."
cd "$SCRIPT_DIR/rasa"
"$VENV_RASA" run actions > "$SCRIPT_DIR/logs/rasa_actions.log" 2>&1 &
RASA_ACTIONS_PID=$!
echo "Rasa Actions Server started with PID $RASA_ACTIONS_PID. Log: logs/rasa_actions.log"
cd "$SCRIPT_DIR"

echo "Starting Python HTTP Server for UI..."
"$VENV_PYTHON" -m http.server 35109 --directory ./UI > "$SCRIPT_DIR/logs/http_server.log" 2>&1 &
HTTP_SERVER_PID=$!
echo "HTTP Server started with PID $HTTP_SERVER_PID. Log: logs/http_server.log"

echo "Starting Main Python Assistant (core/main.py)..."
# Run core/main.py in the foreground so script waits for it
"$VENV_PYTHON" core/main.py

# If core/main.py exits normally (not via Ctrl+C trapped by this script),
# the trap won't be triggered by its exit. So, call cleanup explicitly.
# However, if Ctrl+C is pressed while core/main.py is running, the trap WILL catch it.
cleanup
