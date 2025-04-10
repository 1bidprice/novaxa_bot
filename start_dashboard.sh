#!/bin/bash
# Start script for NOVAXA Web Dashboard on Render

# Make sure the directory structure exists
mkdir -p static/css static/js templates

# Start the Flask application with gunicorn
exec gunicorn integration:app
