#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -e .
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --windowed --name controlwork --paths src run.py
