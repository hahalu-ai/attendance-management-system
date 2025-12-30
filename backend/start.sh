#!/bin/bash
# Railway startup script

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start the application with gunicorn
exec gunicorn run:app --bind 0.0.0.0:${PORT:-5001} --workers 2 --timeout 60
