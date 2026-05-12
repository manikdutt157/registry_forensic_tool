import os
import csv

from core.registry_helpers import get_key, iter_user_hives, iter_values, key_last_write, rot13

USERASSIST = r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist"
APP_COMPAT = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store"

def parse(hives, outdir):
    output = os.path.join(outdir, "Execution_History", "execution_history.csv")
    rows = []

    for user_name, ntuser in iter_user_hives(hives):
        key = get_key(ntuser, USERASSIST)
        if key:
            for guid in key.iter_subkeys():
                count_key = get_key(ntuser, f"{USERASSIST}\\{guid.name}\\Count")
                if not count_key:
                    continue
                last_write = key_last_write(count_key)
                for name, value in iter_values(count_key):
                    rows.append([user_name, "UserAssist", guid.name, last_write, rot13(name), value])

        key = get_key(ntuser, APP_COMPAT)
        if key:
            last_write = key_last_write(key)
            for name, value in iter_values(key):
                rows.append([user_name, "AppCompat", APP_COMPAT, last_write, name, value])

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["user_hive", "source", "key_or_guid", "key_last_write_utc", "item", "raw_value"])
        writer.writerows(rows)
