#!/bin/bash

# Set the folder to the directory where the script is running from
FOLDER=$(dirname "$0")
echo "Folder set to $FOLDER"

# Use find to recursively search for a Python venv
VENV_FOUND=$(find "$FOLDER" -type d \( -name ".venv" -o -name "venv" \))

if [ -z "$VENV_FOUND" ]; then
    echo "No Python venv found. Creating a new one..."
    python -m venv .venv
    source .venv/Scripts/activate
    echo "Installing Python requirements..."
    pip install -r requirements.txt
    echo "Python venv created and requirements installed."
else
    echo "Python venv found at $VENV_FOUND"
    # Activate the venv
    if [ "$SHELL" = "/bin/bash" ]; then
        # Running in Bash
        source "$VENV_FOUND"/Scripts/activate
    elif [ "$SHELL" = "/bin/csh" ] || [ "$SHELL" = "/bin/zsh" ]; then
        # For csh or zsh, use the appropriate activation script
        source "$VENV_FOUND"/Scripts/activate
    else
        echo "Unsupported shell. Please use Bash or Zsh."
    fi
fi
cd "$FOLDER" || exit
