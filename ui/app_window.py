import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from core.acquisition import is_admin, relaunch_as_admin
from ui.buttons import ButtonMixin
from ui.constants import SHELL_BG, SHELL_PANEL
from ui.evidence import EvidenceViewMixin
from ui.reports import ReportMixin
from ui.styles import configure_style
from ui.workers import run_forensics


class ForensicUI(ButtonMixin, EvidenceViewMixin, ReportMixin):
    def __init__(self, root):
        self.root = root
        self.result_tables = {}
        self.category_cards = {}
        self.current_output_path = None
        self.report_format_vars = {
            "pdf": tk.BooleanVar(value=True),
            "docx": tk.BooleanVar(value=True),
            "html": tk.BooleanVar(value=False),
        }

        root.title("Windows Registry Forensic Tool")
        root.geometry("1320x860")
        root.minsize(1120, 740)
        root.configure(background=SHELL_BG)
        root.tk.call("tk", "scaling", 1.35)
        configure_style()

        self._build_shell()
        self._build_evidence_viewer()
        self.show_results()
        self.load_latest_output(silent=True)

    def _build_shell(self):
        header = ttk.Frame(self.root, padding=(22, 18, 22, 14), style="Shell.TFrame")
        header.pack(fill=tk.X)
        header.columnconfigure(0, weight=1)

        title_block = ttk.Frame(header, style="Shell.TFrame")
        title_block.grid(row=0, column=0, sticky="ew")

        title = ttk.Label(title_block, text="Registry Forensic Tool", style="ShellTitle.TLabel")
        title.pack(anchor=tk.W)

        self.output_label = ttk.Label(title_block, text="Case Folder: Not started", style="ShellMuted.TLabel")
        self.output_label.pack(anchor=tk.W, pady=(4, 0))

        actions = ttk.Frame(header, style="Shell.TFrame")
        actions.grid(row=0, column=1, sticky=tk.E)

        self.load_latest_btn = self._create_action_button(
            actions,
            text="Load Latest Case",
            command=self.load_latest_output,
            variant="secondary",
        )
        self.load_latest_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.report_btn = self._create_action_button(
            actions,
            text="Create Report",
            command=self.create_report,
            variant="secondary",
            state="disabled",
        )
        self.report_btn.pack(side=tk.RIGHT, padx=(8, 0))

        self.start_btn = self._create_action_button(
            actions,
            text="Start Forensic Collection",
            command=self.start_process,
            variant="primary",
        )
        self.start_btn.pack(side=tk.RIGHT)

        view_switch = ttk.Frame(self.root, padding=(22, 0, 22, 14), style="Shell.TFrame")
        view_switch.pack(fill=tk.X)

        self.evidence_btn = self._create_nav_button(view_switch, "Evidence", self.show_results)
        self.evidence_btn.pack(side=tk.LEFT)
        self.log_btn = self._create_nav_button(view_switch, "Collection Log", self.show_log)
        self.log_btn.pack(side=tk.LEFT, padx=(8, 0))

        report_options = ttk.Frame(view_switch, style="Shell.TFrame")
        report_options.pack(side=tk.RIGHT)
        tk.Label(
            report_options,
            text="Export:",
            background=SHELL_BG,
            foreground="#d1d5db",
            font=("Segoe UI", 12, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 8))
        for key, label in (("pdf", "PDF"), ("docx", "DOCX"), ("html", "HTML")):
            tk.Checkbutton(
                report_options,
                text=label,
                variable=self.report_format_vars[key],
                background=SHELL_BG,
                activebackground=SHELL_BG,
                foreground="#f9fafb",
                activeforeground="#ffffff",
                selectcolor=SHELL_PANEL,
                font=("Segoe UI", 12),
                borderwidth=0,
            ).pack(side=tk.LEFT, padx=(0, 8))

        self.report_progress = ttk.Progressbar(view_switch, mode="indeterminate", length=150)
        self.report_status = tk.Label(
            view_switch,
            text="",
            background=SHELL_BG,
            foreground="#93c5fd",
            font=("Segoe UI", 11),
        )
        self.report_status.pack(side=tk.RIGHT, padx=(0, 10))

        self.content_frame = ttk.Frame(self.root, padding=(22, 0, 22, 22), style="Shell.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.results_frame = ttk.Frame(self.content_frame, padding=0, style="App.TFrame")
        self.log_frame = ttk.Frame(self.content_frame, padding=0, style="App.TFrame")

        self.log_area = scrolledtext.ScrolledText(
            self.log_frame,
            width=112,
            height=28,
            font=("Cascadia Mono", 12),
            background="#0b1220",
            foreground="#bfdbfe",
            insertbackground="#e2e8f0",
            relief=tk.FLAT,
            borderwidth=0,
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def show_results(self):
        self.active_view = "results"
        self.log_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        self._refresh_nav_buttons()

    def show_log(self):
        self.active_view = "log"
        self.results_frame.pack_forget()
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self._refresh_nav_buttons()

    def log(self, message):
        self.root.after(0, self._append_log, str(message))

    def _append_log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def done(self, output_path):
        def update_ui():
            self._set_action_button_state(self.start_btn, "normal")
            if output_path:
                self.output_label.config(text=f"Case Folder: {output_path}")
                self.load_output(output_path)
                self.show_results()
                self.create_report()

        self.root.after(0, update_ui)

    def start_process(self):
        if not is_admin():
            if messagebox.askyesno(
                "Administrator required",
                "Forensic collection needs Administrator permission.\n\nRestart the app as Administrator?",
            ):
                try:
                    relaunch_as_admin()
                except Exception as exc:
                    messagebox.showerror("Administrator required", f"Please run as Administrator.\n\n{exc}")
            return

        self._set_action_button_state(self.start_btn, "disabled")
        self._set_action_button_state(self.report_btn, "disabled")
        self.output_label.config(text="Case Folder: Running...")
        self.show_log()
        thread = threading.Thread(target=run_forensics, args=(self.log, self.done), daemon=True)
        thread.start()
