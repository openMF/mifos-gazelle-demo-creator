# Define virtual environment directory
venv := ".venv"

# Cross-platform Python path
python := if os() == "windows" { ".venv/Scripts/python.exe" } else { ".venv/bin/python" }

# Install dependencies using uv
install:
    uv venv .venv
    @{{python}} -m ensurepip --upgrade
    @{{python}} -m pip install -e .

# Run the TUI app
create-demo:
    sudo -v
    @{{python}} demo_creator.py

# # Run tests
# test:
#     @{{python}} -m pytest tests/

# # Format using black
# format:
#     @{{python}} -m black demo_creator tests

# Lint using flake8
lint:
    @{{python}} -m flake8 demo_creator tests
