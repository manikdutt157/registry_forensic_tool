import tkinter as tk
import ctypes

from ui.app_window import ForensicUI


def enable_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    enable_dpi_awareness()
    root = tk.Tk()
    ForensicUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
