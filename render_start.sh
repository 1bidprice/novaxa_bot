#!/usr/bin/env bash
# Exit on error
set -o errexit

# Start the Telegram bot in the background
echo "Starting Telegram bot..."
python3 enhanced_bot.py &

# Start the Flask dashboard using Gunicorn
# Render will set the PORT environment variable
echo "Starting dashboard on port $PORT with debug logging..."
gunicorn enhanced_bot:app --bind 0.0.0.0:${PORT:-10000} --log-level debug
