import os
import csv

from core.registry_helpers import get_key, get_system_control_sets, iter_values, key_last_write

def parse(hives, outdir):
    system = hives.get("SYSTEM")
    if not system:
        return

    output = os.path.join(outdir, "USB_History", "usb_devices.csv")
    rows = []

    for control_set in get_system_control_sets(system):
        usb_key = get_key(system, rf"{control_set}\Enum\USBSTOR")
        if not usb_key:
            continue
        for device in usb_key.iter_subkeys():
            for instance in device.iter_subkeys():
                values = dict(iter_values(instance))
                rows.append([
                    control_set,
                    device.name,
                    key_last_write(device),
                    instance.name,
                    key_last_write(instance),
                    values.get("FriendlyName", ""),
                    values.get("ParentIdPrefix", ""),
                    values.get("ContainerID", ""),
                ])

    with open(output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "control_set",
            "device_type",
            "device_key_last_write_utc",
            "instance_id",
            "instance_key_last_write_utc",
            "friendly_name",
            "parent_id_prefix",
            "container_id",
        ])
        writer.writerows(rows)
