from pathlib import Path
from tempfile import TemporaryDirectory

from core.acquisition import acquire_hives, create_shadow_copy
from core.hive_loader import load_hives
from core.parser_engine import run_all_parsers
from core.utils import create_output_structure


def run_forensics(log, done, save_dir: str = None):
    output_path = None
    try:
        shadow = create_shadow_copy(log)
        if not shadow:
            return

        outdir = create_output_structure(base_dir=save_dir)
        with TemporaryDirectory(prefix="hives_", dir=outdir) as hive_dir:
            hive_paths = acquire_hives(shadow, log, Path(hive_dir))
            if not hive_paths:
                log("[-] No hives were acquired.")
                return

            log("\n[+] Starting Registry Parsing...\n")

            hives = load_hives(hive_paths, log)
            run_all_parsers(hives, outdir, log)

        output_path = Path(outdir).resolve()
        log("\n[+] Parsing Completed!")
        log(f"[+] Evidence saved at: {output_path}")
    except Exception as exc:
        log(f"[-] Fatal error: {exc}")
    finally:
        done(output_path)
