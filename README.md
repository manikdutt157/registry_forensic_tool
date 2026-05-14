# Windows Registry Forensic Tool

A small Windows registry acquisition and parsing utility built around `regipy`.

## Requirements

- Windows
- Administrator privileges
- Python dependencies from `requirements.txt`

## Run the App

```powershell
.\venv\Scripts\python.exe app.py
```

The GUI will request elevation if it is not already running as Administrator.

## Run the CLI

```powershell
.\venv\Scripts\python.exe main.py
```

## Output

The tool creates a Volume Shadow Copy, stages available registry hives temporarily, and writes parsed evidence into timestamped case folders under `C:\Forensic_Report`.

Generated parser outputs are CSV files for:

- Persistence run keys
- USB storage history
- System information
- User activity
- Execution history
- Network profiles

The GUI can also load the latest case folder and create reports from the parsed CSV evidence. Reports are saved under the selected case folder in `Reports`, for example `C:\Forensic_Report\CASE_YYYYMMDD_HHMMSS\Reports`.

Before creating a report, the GUI asks for report details such as case name, case number, investigator name, organization, evidence ID, subject, examination date, and notes. These details are added as a dedicated report details page.

The report exporter supports:

- PDF (`.pdf`)
- Word DOCX (`.docx`)
