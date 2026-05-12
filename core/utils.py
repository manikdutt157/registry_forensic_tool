import os
from datetime import datetime
from pathlib import Path

def create_output_structure():
    base = Path("output") / f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    folders = [
        "Persistence",
        "USB_History",
        "System_Info",
        "User_Activity",
        "Execution_History",
        "Network_Info"
    ]
    for f in folders:
        os.makedirs(base / f, exist_ok=True)
    return str(base)
