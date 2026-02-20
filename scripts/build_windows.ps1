Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    & py -3.11 --version | Out-Null
} catch {
    Write-Error "Python 3.11 is required. Install it first (e.g. winget install Python.Python.3.11)."
    exit 1
}

& py -3.11 -m pip install --upgrade pip
& py -3.11 -m pip install -e .
& py -3.11 -m pip install pyinstaller
& py -3.11 -m PyInstaller --noconfirm --windowed --name ControlWork --paths src run.py
