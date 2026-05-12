import codecs
from datetime import datetime, timezone
from typing import Iterable, Iterator, Tuple


def safe_value(value):
    data = getattr(value, "value", "")
    if isinstance(data, bytes):
        try:
            return data.decode("utf-16-le").rstrip("\x00")
        except UnicodeDecodeError:
            return data.hex()
    return data


def safe_value_name(value):
    name = getattr(value, "name", "")
    return "(Default)" if name in ("", None) else str(name)


def iter_values(key) -> Iterator[Tuple[str, object]]:
    if not key:
        return
    values = key.iter_values() if hasattr(key, "iter_values") else getattr(key, "values", [])
    for value in values or []:
        yield safe_value_name(value), safe_value(value)


def get_key(hive, path):
    try:
        if path in ("", None):
            path = "\\"
        elif not str(path).startswith("\\"):
            path = f"\\{path}"
        return hive.get_key(path)
    except Exception:
        return None


def key_last_write(key):
    try:
        timestamp = key.header.last_modified
    except Exception:
        return ""
    return filetime_to_iso(timestamp)


def filetime_to_iso(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    if value <= 0:
        return ""
    try:
        seconds = (value - 116444736000000000) / 10000000
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return ""


def unix_seconds_to_iso(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    if value <= 0:
        return ""
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return ""


def registry_systemtime_to_iso(value):
    if isinstance(value, bytes):
        raw = value
    else:
        text = str(value).strip()
        try:
            raw = bytes.fromhex(text)
        except ValueError:
            return ""

    if len(raw) < 16:
        return ""

    try:
        year = int.from_bytes(raw[0:2], "little")
        month = int.from_bytes(raw[2:4], "little")
        day = int.from_bytes(raw[6:8], "little")
        hour = int.from_bytes(raw[8:10], "little")
        minute = int.from_bytes(raw[10:12], "little")
        second = int.from_bytes(raw[12:14], "little")
        millisecond = int.from_bytes(raw[14:16], "little")
        return datetime(year, month, day, hour, minute, second, millisecond * 1000, tzinfo=timezone.utc).isoformat()
    except ValueError:
        return ""


def iter_user_hives(hives: dict) -> Iterator[Tuple[str, object]]:
    for name, hive in hives.items():
        if name == "NTUSER" or name.startswith("NTUSER_"):
            yield name, hive


def get_system_control_sets(system_hive) -> Iterable[str]:
    select_key = get_key(system_hive, "Select")
    current = None
    if select_key:
        for name, value in iter_values(select_key):
            if name == "Current":
                try:
                    current = int(value)
                except (TypeError, ValueError):
                    current = None
                break

    if current:
        preferred = f"ControlSet{current:03d}"
        if get_key(system_hive, preferred):
            yield preferred
            return

    root = get_key(system_hive, "")
    if not root:
        return

    for subkey in root.iter_subkeys():
        if subkey.name.startswith("ControlSet"):
            yield subkey.name


def rot13(text):
    return codecs.decode(str(text), "rot_13")
