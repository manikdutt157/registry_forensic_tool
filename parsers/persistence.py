import os
import csv

from core.registry_helpers import get_key, iter_user_hives, iter_values, key_last_write

RUN_KEYS = [
    ("SOFTWARE", r"Microsoft\Windows\CurrentVersion\Run"),
    ("SOFTWARE", r"Microsoft\Windows\CurrentVersion\RunOnce"),
    ("SOFTWARE", r"Wow6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ("SOFTWARE", r"Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce"),
]

def parse(hives, outdir):
    output = os.path.join(outdir, "Persistence", "run_keys.csv")
    rows = []

    for hive_name, path in RUN_KEYS:
        hive = hives.get(hive_name)
        key = get_key(hive, path) if hive else None
        if not key:
            continue
        last_write = key_last_write(key)
        for name, value in iter_values(key):
            rows.append([hive_name, path, last_write, name, value])

    for user_name, hive in iter_user_hives(hives):
        for path in (
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
        ):
            key = get_key(hive, path)
            if not key:
                continue
            last_write = key_last_write(key)
            for name, value in iter_values(key):
                rows.append([user_name, path, last_write, name, value])

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["hive", "key_path", "key_last_write_utc", "value_name", "value"])
        writer.writerows(rows)
