#!/usr/bin/env bash
# start-display.sh — Launch the DnD cinematic display companion
# Starts app.py in the background if not already running, then opens the browser.

DISPLAY_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DISPLAY_DIR/app.log"
PID_FILE="$DISPLAY_DIR/app.pid"
URL="http://localhost:5001"

# Check if already running
if curl -s "$URL/ping" > /dev/null 2>&1; then
    echo "Display already running at $URL"
    open "$URL" 2>/dev/null || true
    exit 0
fi

# Start Flask server in background
nohup python3 "$DISPLAY_DIR/app.py" > "$LOG" 2>&1 &
echo $! > "$PID_FILE"

# Wait up to 5 seconds for the server to become ready
for i in $(seq 1 10); do
    sleep 0.5
    if curl -s "$URL/ping" > /dev/null 2>&1; then
        echo "Display started — $URL"
        open "$URL" 2>/dev/null || true
        exit 0
    fi
done

echo "Warning: display server may not have started. Check $LOG for details."
exit 1
