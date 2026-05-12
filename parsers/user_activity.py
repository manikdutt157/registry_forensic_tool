import os
import csv

from core.registry_helpers import get_key, iter_user_hives, iter_values, key_last_write

USER_KEYS = [
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
    r"Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
]

def parse(hives, outdir):
    output = os.path.join(outdir, "User_Activity", "recent_activity.csv")
    rows = []

    for user_name, ntuser in iter_user_hives(hives):
        for path in USER_KEYS:
            key = get_key(ntuser, path)
            if not key:
                continue
            last_write = key_last_write(key)
            for name, value in iter_values(key):
                rows.append([user_name, path, last_write, name, value])

            for subkey in key.iter_subkeys():
                subkey_path = f"{path}\\{subkey.name}"
                subkey_last_write = key_last_write(subkey)
                for name, value in iter_values(subkey):
                    rows.append([user_name, subkey_path, subkey_last_write, name, value])

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_hive", "key_path", "key_last_write_utc", "value_name", "value"])
        writer.writerows(rows)
