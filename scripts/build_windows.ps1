python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --windowed --name ControlWork --paths src run.py
