# PowerShell equivalent of install_dependencies.sh
Write-Host "Setting up your system..."

# Check for Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "Python not found. Download and install from: https://www.python.org/downloads/windows/"
    exit 1
}

Write-Host "Python found: $pythonCmd"

# Check for pip
if (-not (Get-Command pip -ErrorAction SilentlyContinue) -and -not (Get-Command pip3 -ErrorAction SilentlyContinue)) {
    Write-Host "pip not found. Installing using ensurepip..."
    & $pythonCmd -m ensurepip --upgrade
    & $pythonCmd -m pip install --upgrade pip
} else {
    Write-Host "pip is available."
}

# Install uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing..."
    iwr https://astral.sh/uv/install.ps1 -UseBasicParsing | iex
} else {
    Write-Host "uv already installed."
}

# Install just
if (-not (Get-Command just -ErrorAction SilentlyContinue)) {
    Write-Host "just not found. Installing..."
    iwr https://just.systems/install.ps1 -UseBasicParsing | iex
} else {
    Write-Host "just is already installed."
}

Write-Host ""
Write-Host "All tools are ready!"
Write-Host "Next steps:"
Write-Host "    just setup"
Write-Host "    just run"