import sys
from pathlib import Path

from core.acquisition import acquire_hives, create_shadow_copy, is_admin
from core.hive_loader import load_hives
from core.parser_engine import run_all_parsers
from core.utils import create_output_structure


def main():
    print("=== Windows Registry Forensic Tool ===")

    if not is_admin():
        print("\n[!] Run this script from an elevated Administrator terminal.\n")
        sys.exit(1)

    shadow = create_shadow_copy()
    if not shadow:
        sys.exit(1)

    hive_paths = acquire_hives(shadow)
    if not hive_paths:
        print("[-] No hives were acquired.")
        sys.exit(1)

    print("\n[+] Hive acquisition done. Starting parsing...\n")

    outdir = create_output_structure()
    hives = load_hives(hive_paths)
    run_all_parsers(hives, outdir)

    print(f"\n[+] Parsing completed. Evidence saved at: {Path(outdir).resolve()}")


if __name__ == "__main__":
    main()
