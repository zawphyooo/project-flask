#!/bin/sh

# Activate the virtual environment
source flaskenv/bin/activate

# Set environment variables
export FLASK_APP=app
export FLASK_DEBUG=1

# Run Flask application
flask run --host=192.168.1.119 --port=5005
