#!/bin/bash
# render_start.sh - Script to start the Telegram bot on Render platform

# Set up environment
echo "Setting up environment for Telegram bot on Render platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if required files exist
if [ ! -f "enhanced_bot.py" ]; then
    echo "Error: enhanced_bot.py not found."
    exit 1
fi

if [ ! -f "api.py" ]; then
    echo "Error: api.py not found."
    exit 1
fi

if [ ! -f "integration.py" ]; then
    echo "Error: integration.py not found."
    exit 1
fi

if [ ! -f "monitor.py" ]; then
    echo "Error: monitor.py not found."
    exit 1
fi

# Check if .env file exists, create if not
if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env << EOF
# Telegram Bot Configuration
DEBUG=true
LOG_LEVEL=INFO
WEBHOOK_ENABLED=true
PORT=8443
EOF
    echo ".env file created."
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Installing default dependencies..."
    pip install python-telegram-bot requests psutil
fi

# Check for Telegram token in environment variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "Warning: TELEGRAM_BOT_TOKEN environment variable not set."
    echo "Please set the TELEGRAM_BOT_TOKEN environment variable in the Render dashboard."
    echo "For testing purposes, a placeholder token will be used."
    export TELEGRAM_BOT_TOKEN="placeholder_token"
fi

# Set up logging directory
mkdir -p logs

# Start the bot
echo "Starting Telegram bot..."
python3 enhanced_bot.py

# Exit with the same status as the bot
exit $?
