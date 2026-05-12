import os
import csv

from core.registry_helpers import get_key, iter_values, key_last_write, registry_systemtime_to_iso

NET_KEY = r"Microsoft\Windows NT\CurrentVersion\NetworkList\Profiles"

def parse(hives, outdir):
    software = hives.get("SOFTWARE")
    if not software:
        return

    output = os.path.join(outdir, "Network_Info", "network_profiles.csv")
    rows = []

    key = get_key(software, NET_KEY)
    if key:
        for profile in key.iter_subkeys():
            values = dict(iter_values(profile))
            date_created_raw = values.get("DateCreated", "")
            date_last_connected_raw = values.get("DateLastConnected", "")
            rows.append([
                profile.name,
                key_last_write(profile),
                values.get("ProfileName", ""),
                values.get("Description", ""),
                values.get("Managed", ""),
                date_created_raw,
                registry_systemtime_to_iso(date_created_raw),
                date_last_connected_raw,
                registry_systemtime_to_iso(date_last_connected_raw),
            ])

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "profile_guid",
            "key_last_write_utc",
            "profile_name",
            "description",
            "managed",
            "date_created_raw",
            "date_created_utc",
            "date_last_connected_raw",
            "date_last_connected_utc",
        ])
        writer.writerows(rows)
