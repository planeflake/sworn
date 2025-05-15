#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install FastAPI Swagger Dark theme if not already installed
pip install fastapi-swagger-dark

# Run the application
python -m app.main