import os
from datetime import datetime
from pathlib import Path


DEFAULT_OUTPUT_ROOT = Path(r"C:\Forensic_Report")


def create_output_structure(base_dir: str = None):
    """Create a CASE_<timestamp> folder structure.

    If `base_dir` is provided, the CASE_<timestamp> folder will be created
    under that directory. Otherwise the default C:\\Forensic_Report folder is used.
    Returns the created base path as a string.
    """
    if base_dir:
        base = Path(base_dir) / f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        base = DEFAULT_OUTPUT_ROOT / f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    folders = [
        "Persistence",
        "USB_History",
        "System_Info",
        "User_Activity",
        "Execution_History",
        "Network_Info",
    ]

    for f in folders:
        os.makedirs(base / f, exist_ok=True)

    return str(base)
