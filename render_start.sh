#!/bin/bash
# Script to keep the bot running on Render
# This avoids the 403/409 errors by implementing a keep-alive mechanism

# Make script executable
chmod +x render_start.sh

# Start the Flask application with gunicorn
exec gunicorn enhanced_bot:app
