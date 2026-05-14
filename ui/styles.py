from tkinter import ttk

from ui.constants import INK, MUTED, PAGE_BG, REPORT_BLUE, SHELL_BG, TEXT_BG


def configure_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Shell.TFrame", background=SHELL_BG)
    style.configure("App.TFrame", background=PAGE_BG)
    style.configure("Report.TFrame", background=PAGE_BG)
    style.configure("Panel.TFrame", background=TEXT_BG)
    style.configure("TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 12))
    style.configure("ShellTitle.TLabel", background=SHELL_BG, foreground="#ffffff", font=("Segoe UI", 26, "bold"))
    style.configure("ShellMuted.TLabel", background=SHELL_BG, font=("Segoe UI", 12), foreground="#d1d5db")
    style.configure("Title.TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 22, "bold"))
    style.configure("Muted.TLabel", background=PAGE_BG, font=("Segoe UI", 12), foreground=MUTED)
    style.configure("ReportBlue.TLabel", background=PAGE_BG, foreground=REPORT_BLUE, font=("Consolas", 12))
    style.configure("Meta.TLabel", background=TEXT_BG, foreground=REPORT_BLUE, font=("Consolas", 12))
    style.configure(
        "Treeview",
        rowheight=40,
        font=("Segoe UI", 12),
        background=TEXT_BG,
        fieldbackground=TEXT_BG,
        foreground=INK,
        borderwidth=1,
        relief="solid",
    )
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#111827", foreground="#ffffff")
    style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", INK)])
    style.configure("DashboardTitle.TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 24, "bold"))
    style.configure("SectionTitle.TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 14, "bold"))
    style.configure("Back.TButton", padding=(10, 5))
