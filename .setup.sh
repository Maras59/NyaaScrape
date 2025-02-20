#!/bin/bash

# Define the virtual environment directory
VENV_DIR="venv"

# Check if Python is installed
if ! command -v python3.12 &> /dev/null; then
    echo "Python3.12 is not installed. Please install it first."
    exit 1
fi

# Create the virtual environment
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created in $VENV_DIR."
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Dependencies installed."
else
    echo "No requirements.txt found. Skipping dependency installation."
fi

deactivate
