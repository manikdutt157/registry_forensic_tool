from regipy.registry import RegistryHive

def load_hives(paths: dict, log=print):
    hives = {}
    for name, path in paths.items():
        try:
            hive = RegistryHive(path)
            hives[name] = hive
            log(f"[+] Loaded {name}")
        except Exception as e:
            log(f"[-] Failed to load {name}: {e}")
    return hives
