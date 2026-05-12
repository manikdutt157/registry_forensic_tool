from pathlib import Path
import os
import runpy


APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)
runpy.run_path(str(APP_DIR / "ui.py"), run_name="__main__")
