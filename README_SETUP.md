Setup (recommended): use Python 3.12

This project has been developed against Python 3.12 / Flask and SQLAlchemy versions compatible with that runtime.

Quick steps (PowerShell):

1) Install Python 3.12 (if not installed). You can download from https://www.python.org/downloads/release/python-312x/ or use a version manager.

2) Create a virtual environment and activate it:

```powershell
# Adjust python executable if required. Example using py launcher:
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Or if python3.12 is on PATH:
python3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install pinned dependencies:

```powershell
pip install -U pip
pip install -r requirements.txt
```

4) Run the app:

```powershell
python run.py
# Open http://127.0.0.1:5000 in your browser
```

Notes / alternatives:
- If you cannot install Python 3.12 on the machine, I can try to pin libraries differently, but SQLAlchemy and typing changes in Python 3.14 currently cause import-time errors. The safest path is to use Python 3.12.
- After you have the venv running I can re-run the unit tests and start the server from here to verify the `market_type` persistence and the confetti UI changes.
