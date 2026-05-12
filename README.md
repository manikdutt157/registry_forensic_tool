# Windows Registry Forensic Tool

A small Windows registry acquisition and parsing utility built around `regipy`.

## Requirements

- Windows
- Administrator privileges
- Python dependencies from `requirements.txt`

## Run the GUI

```powershell
.\venv\Scripts\python.exe ui.py
```

The GUI will request elevation if it is not already running as Administrator.

## Run the CLI

```powershell
.\venv\Scripts\python.exe main.py
```

## Output

The tool creates a Volume Shadow Copy, copies available registry hives into `acquired_hives`, and writes parsed evidence into timestamped folders under `output`.

Generated parser outputs are CSV files for:

- Persistence run keys
- USB storage history
- System information
- User activity
- Execution history
- Network profiles

The GUI can also load the latest case folder and create an HTML report from the parsed CSV evidence. Reports are saved under the selected case folder in `Reports`.

The report exporter supports:

- HTML (`.html`)
- PDF (`.pdf`)
- Word DOCX (`.docx`)
