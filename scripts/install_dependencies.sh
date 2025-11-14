#!/bin/bash
set -e

echo "Setting up your system..."

OS="$(uname -s)"

if [[ "$OS" == "MINGW"* || "$OS" == "CYGWIN"* || "$OS" == "MSYS"* ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

# ------------------------
# Step 1: Check for Python
# ------------------------
if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
    echo "Python not found."
    if [ "$IS_WINDOWS" = true ]; then
        echo "Download and install Python manually from:"
        echo "    https://www.python.org/downloads/windows/"
    else
        echo "Install Python using your package manager:"
        echo "    macOS: brew install python"
        echo "    Debian/Ubuntu: sudo apt install python3 python3-pip"
        echo "    Arch: sudo pacman -S python"
    fi
    exit 1
fi

# Set PYTHON command
if command -v python3 &>/dev/null; then
    PYTHON=$(command -v python3)
else
    PYTHON=$(command -v python)
fi

# ------------------------
# Step 2: Check for pip
# ------------------------
if ! command -v pip &>/dev/null && ! command -v pip3 &>/dev/null; then
    echo "pip not found. Installing using ensurepip..."
    $PYTHON -m ensurepip --upgrade
    $PYTHON -m pip install --upgrade pip
else
    echo "pip is available."
fi

# ------------------------
# Step 3: Install uv
# ------------------------
if ! command -v uv &>/dev/null; then
    echo "uv not found. Installing..."
    if [ "$IS_WINDOWS" = true ]; then
        echo "Running Windows uv install script..."
        powershell -Command "iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex"
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
else
    echo "uv already installed."
fi

# ------------------------
# Step 4: Install just
# ------------------------
if ! command -v just &>/dev/null; then
    echo "just not found. Installing..."
    if [ "$IS_WINDOWS" = true ]; then
        echo "Installing just for Windows (to ~/.cargo/bin)..."
        powershell -Command "iwr https://just.systems/install.ps1 -UseBasicParsing | iex"
    else
        curl -sSf https://just.systems/install.sh | bash -s -- --to ~/.cargo/bin
        export PATH="$HOME/.cargo/bin:$PATH"
        echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
    fi
else
    echo "just is already installed."
fi

# ------------------------
# Final instructions
# ------------------------
echo
echo "All tools are ready!"
echo "Next steps:"
echo "    just setup"
echo "    just run"
echo
