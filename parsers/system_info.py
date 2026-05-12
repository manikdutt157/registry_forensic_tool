import os
import csv

from core.registry_helpers import get_key, iter_values

SYS_KEY = r"Microsoft\Windows NT\CurrentVersion"
COMPUTER_NAME_KEY = r"ControlSet001\Control\ComputerName\ComputerName"

def parse(hives, outdir):
    software = hives.get("SOFTWARE")
    system = hives.get("SYSTEM")

    output = os.path.join(outdir, "System_Info", "system_info.csv")
    rows = []

    key = get_key(software, SYS_KEY) if software else None
    if key:
        wanted = {
            "ProductName",
            "EditionID",
            "CurrentBuild",
            "CurrentBuildNumber",
            "DisplayVersion",
            "ReleaseId",
            "InstallDate",
            "RegisteredOwner",
            "SystemRoot",
        }
        for name, value in iter_values(key):
            if name in wanted:
                rows.append(["SOFTWARE", SYS_KEY, name, value])

    key = get_key(system, COMPUTER_NAME_KEY) if system else None
    if key:
        for name, value in iter_values(key):
            rows.append(["SYSTEM", COMPUTER_NAME_KEY, name, value])

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["hive", "key_path", "value_name", "value"])
        writer.writerows(rows)
