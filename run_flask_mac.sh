#!/bin/bash
source flaskenv/bin/activate
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000
