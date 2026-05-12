from parsers import (
    persistence,
    usb_history,
    system_info,
    user_activity,
    execution_history,
    network_info
)

PARSERS = (
    ("Persistence", persistence),
    ("USB History", usb_history),
    ("System Info", system_info),
    ("User Activity", user_activity),
    ("Execution History", execution_history),
    ("Network Info", network_info),
)


def run_all_parsers(hives, outdir, log=print):
    for name, parser in PARSERS:
        try:
            log(f"[>] Running parser: {name}")
            parser.parse(hives, outdir)
        except Exception as exc:
            log(f"[-] Parser failed ({name}): {exc}")
