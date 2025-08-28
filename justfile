# Define virtual environment directory
venv := ".venv"

# Cross-platform Python path
python := if os() == "windows" { ".venv/Scripts/python.exe" } else { ".venv/bin/python" }

# Install dependencies using uv
setup:
    uv venv .venv
    @{{python}} -m ensurepip --upgrade
    @{{python}} -m pip install -e .

# Run the TUI app
run:
    sudo -v
    @{{python}} main.py

# Clean virtualenv and cache
clean:
    find . -type d -name "__pycache__" -exec rm -rf {} +
    rm -rf .venv *.pyc *.egg-info .mypy_cache .pytest_cache

# Run tests
test:
    @{{python}} -m pytest tests/

# Format using black
format:
    @{{python}} -m black demo_creator tests

# Lint using flake8
lint:
    @{{python}} -m flake8 demo_creator tests
