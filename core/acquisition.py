import ctypes
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Optional


HIVE_DEST = Path("acquired_hives")
SYSTEM_HIVES = ("SYSTEM", "SOFTWARE", "SAM", "SECURITY")


def default_log(message: str) -> None:
    print(message)


def is_windows() -> bool:
    return os.name == "nt"


def is_admin() -> bool:
    if not is_windows():
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin(target_script: Optional[str] = None) -> None:
    script = target_script or sys.argv[0]
    executable = Path(sys.executable)
    if executable.name.lower() == "python.exe":
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.exists():
            executable = pythonw
    ctypes.windll.shell32.ShellExecuteW(None, "runas", str(executable), f'"{script}"', None, 1)
    sys.exit()


def run_command(args, log: Callable[[str], None] = default_log) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(args, capture_output=True, text=True)
    except FileNotFoundError as exc:
        log(f"[-] Command not found: {args[0]}")
        return subprocess.CompletedProcess(args, 127, "", str(exc))
    if result.stdout.strip():
        log(result.stdout.strip())
    if result.stderr.strip():
        log(result.stderr.strip())
    return result


def create_shadow_copy(log: Callable[[str], None] = default_log) -> Optional[str]:
    log("[+] Creating Volume Shadow Copy for C: ...")
    result = run_command(
        ["wmic", "shadowcopy", "call", "create", 'Volume="C:\\"'],
        log,
    )
    if result.returncode != 0:
        log("[!] WMIC shadow creation failed; trying vssadmin.")
        result = run_command(["vssadmin", "create", "shadow", "/for=C:"], log)
        if result.returncode != 0:
            log("[-] Failed to create a shadow copy. Run as Administrator and ensure VSS is available.")
            return None

    list_result = run_command(["vssadmin", "list", "shadows"], log)
    matches = re.findall(r"Shadow Copy Volume:\s*(.+)", list_result.stdout)
    if not matches:
        log("[-] Could not locate the shadow copy path.")
        return None

    shadow_path = matches[-1].strip().rstrip("\\")
    log(f"[+] Shadow Path Found: {shadow_path}")
    return shadow_path


def copy_file(src: Path, dst: Path, log: Callable[[str], None] = default_log) -> bool:
    try:
        if not src.exists():
            log(f"[-] Missing source: {src}")
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        log(f"[+] Copied: {dst}")
        return True
    except Exception as exc:
        log(f"[-] Failed to copy {src}: {exc}")
        return False


def acquire_hives(shadow_path: str, log: Callable[[str], None] = default_log) -> Dict[str, str]:
    HIVE_DEST.mkdir(parents=True, exist_ok=True)
    acquired: Dict[str, str] = {}

    config_path = Path(shadow_path) / "Windows" / "System32" / "config"
    users_path = Path(shadow_path) / "Users"

    for hive in SYSTEM_HIVES:
        dst = HIVE_DEST / hive
        if copy_file(config_path / hive, dst, log):
            acquired[hive] = str(dst)

    local_users = Path(os.environ.get("SystemDrive", "C:") + "\\Users")
    user_names = [p.name for p in local_users.iterdir() if p.is_dir()] if local_users.exists() else []
    for user in user_names:
        ntuser_src = users_path / user / "NTUSER.DAT"
        ntuser_dst = HIVE_DEST / f"NTUSER_{user}.DAT"
        if copy_file(ntuser_src, ntuser_dst, log):
            acquired[f"NTUSER_{user}"] = str(ntuser_dst)

    return acquired


def discover_acquired_hives(base: Path = HIVE_DEST) -> Dict[str, str]:
    paths: Dict[str, str] = {}
    for hive in SYSTEM_HIVES:
        path = base / hive
        if path.exists():
            paths[hive] = str(path)
    for path in sorted(base.glob("NTUSER_*.DAT")):
        paths[path.stem] = str(path)
    return paths
