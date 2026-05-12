import csv
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

from core.acquisition import acquire_hives, create_shadow_copy, is_admin, relaunch_as_admin
from core.hive_loader import load_hives
from core.parser_engine import run_all_parsers
from core.report_generator import generate_reports
from core.utils import create_output_structure


PAGE_BG = "#f3f6fb"
SHELL_BG = "#0f172a"
SHELL_PANEL = "#111c34"
PANEL_BG = "#ffffff"
TEXT_BG = "#ffffff"
INK = "#172033"
MUTED = "#64748b"
REPORT_BLUE = "#2563eb"
BORDER = "#d8e0ec"
CARD_SHADOW = "#d5deec"
CARD_HOVER = "#f8fbff"
SUCCESS = "#10b981"

RESULT_TABS = (
    (
        "System Info",
        "System_Info",
        "system_info.csv",
        "Host identity, Windows version, install data, and computer name values.",
        "SYSTEM",
        "#2563eb",
    ),
    (
        "User Activity",
        "User_Activity",
        "recent_activity.csv",
        "Recent documents, typed paths, RunMRU, and open/save activity.",
        "ACTIVITY",
        "#059669",
    ),
    (
        "Execution History",
        "Execution_History",
        "execution_history.csv",
        "UserAssist and AppCompat traces that show program execution evidence.",
        "EXECUTION",
        "#7c3aed",
    ),
    (
        "Persistence",
        "Persistence",
        "run_keys.csv",
        "Run and RunOnce registry entries used for autorun persistence.",
        "AUTORUN",
        "#dc2626",
    ),
    (
        "USB History",
        "USB_History",
        "usb_devices.csv",
        "USB storage devices, instance IDs, friendly names, and timestamps.",
        "USB",
        "#d97706",
    ),
    (
        "Network Info",
        "Network_Info",
        "network_profiles.csv",
        "Known network profiles, creation dates, and last connection times.",
        "NETWORK",
        "#0891b2",
    ),
)

CATEGORY_ITEMS = {
    "System Info": ("Computer Name", "Windows Version", "Install Details", "Registered Owner"),
    "User Activity": ("Recent Documents", "Typed Paths", "Run Commands", "Opened/Saved Files"),
    "Execution History": ("UserAssist", "AppCompat Store", "Decoded Program Names", "Raw Values"),
    "Persistence": ("Run Keys", "RunOnce Keys", "User Autoruns", "System Autoruns"),
    "USB History": ("USB Devices", "Device Types", "Instance IDs", "Friendly Names"),
    "Network Info": ("Network Profiles", "Profile Names", "Created Time", "Last Connected"),
}


def run_forensics(log, done):
    output_path = None
    try:
        shadow = create_shadow_copy(log)
        if not shadow:
            return

        hive_paths = acquire_hives(shadow, log)
        if not hive_paths:
            log("[-] No hives were acquired.")
            return

        log("\n[+] Starting Registry Parsing...\n")

        outdir = create_output_structure()
        hives = load_hives(hive_paths, log)
        run_all_parsers(hives, outdir, log)

        output_path = Path(outdir).resolve()
        log("\n[+] Parsing Completed!")
        log(f"[+] Evidence saved at: {output_path}")
    except Exception as exc:
        log(f"[-] Fatal error: {exc}")
    finally:
        done(output_path)


class ForensicUI:
    def __init__(self, root):
        self.root = root
        self.result_tables = {}
        self.category_cards = {}
        self.current_output_path = None
        self.report_format_vars = {
            "pdf": tk.BooleanVar(value=True),
            "docx": tk.BooleanVar(value=True),
            "xlsx": tk.BooleanVar(value=False),
        }
        root.title("Windows Registry Forensic Tool")
        root.geometry("1180x760")
        root.minsize(920, 620)
        root.configure(background=SHELL_BG)
        self._configure_style()

        header = ttk.Frame(root, padding=(22, 18, 22, 14), style="Shell.TFrame")
        header.pack(fill=tk.X)
        header.columnconfigure(0, weight=1)

        title_block = ttk.Frame(header, style="Shell.TFrame")
        title_block.grid(row=0, column=0, sticky="ew")

        title = ttk.Label(title_block, text="Registry Forensic Tool", style="ShellTitle.TLabel")
        title.pack(anchor=tk.W)

        self.output_label = ttk.Label(title_block, text="Output Folder: Not started", style="ShellMuted.TLabel")
        self.output_label.pack(anchor=tk.W, pady=(4, 0))

        actions = ttk.Frame(header, style="Shell.TFrame")
        actions.grid(row=0, column=1, sticky=tk.E)

        self.load_latest_btn = self._create_action_button(
            actions,
            text="Load Latest Output",
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

        view_switch = ttk.Frame(root, padding=(22, 0, 22, 14), style="Shell.TFrame")
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
            foreground="#a9b7cc",
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 8))
        for key, label in (("pdf", "PDF"), ("docx", "DOCX"), ("xlsx", "Excel")):
            tk.Checkbutton(
                report_options,
                text=label,
                variable=self.report_format_vars[key],
                background=SHELL_BG,
                activebackground=SHELL_BG,
                foreground="#dbeafe",
                activeforeground="#ffffff",
                selectcolor=SHELL_PANEL,
                font=("Segoe UI", 9),
                borderwidth=0,
            ).pack(side=tk.LEFT, padx=(0, 8))

        self.report_progress = ttk.Progressbar(view_switch, mode="indeterminate", length=150)
        self.report_status = tk.Label(
            view_switch,
            text="",
            background=SHELL_BG,
            foreground="#93c5fd",
            font=("Segoe UI", 9),
        )
        self.report_status.pack(side=tk.RIGHT, padx=(0, 10))

        self.content_frame = ttk.Frame(root, padding=(22, 0, 22, 22), style="Shell.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.results_frame = ttk.Frame(self.content_frame, padding=0, style="App.TFrame")
        self.log_frame = ttk.Frame(self.content_frame, padding=0, style="App.TFrame")

        self.log_area = scrolledtext.ScrolledText(
            self.log_frame,
            width=112,
            height=28,
            font=("Cascadia Mono", 10),
            background="#0b1220",
            foreground="#93c5fd",
            insertbackground="#e2e8f0",
            relief=tk.FLAT,
            borderwidth=0,
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        self._build_evidence_viewer()
        self.show_results()
        self.load_latest_output(silent=True)

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Shell.TFrame", background=SHELL_BG)
        style.configure("App.TFrame", background=PAGE_BG)
        style.configure("Report.TFrame", background=PAGE_BG)
        style.configure("Panel.TFrame", background=PANEL_BG)
        style.configure("TLabel", background=PAGE_BG, foreground=INK)
        style.configure("ShellTitle.TLabel", background=SHELL_BG, foreground="#f8fafc", font=("Segoe UI", 20, "bold"))
        style.configure("ShellMuted.TLabel", background=SHELL_BG, font=("Segoe UI", 10), foreground="#a9b7cc")
        style.configure("Title.TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 18, "bold"))
        style.configure("Muted.TLabel", background=PAGE_BG, font=("Segoe UI", 10), foreground=MUTED)
        style.configure("ReportBlue.TLabel", background=PAGE_BG, foreground=REPORT_BLUE, font=("Consolas", 10))
        style.configure("Meta.TLabel", background=TEXT_BG, foreground=REPORT_BLUE, font=("Consolas", 10))
        style.configure(
            "Treeview",
            rowheight=30,
            font=("Segoe UI", 9),
            background=TEXT_BG,
            fieldbackground=TEXT_BG,
            foreground=INK,
            borderwidth=0,
        )
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#1e293b", foreground="#ffffff")
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", INK)])
        style.configure("DashboardTitle.TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 18, "bold"))
        style.configure("SectionTitle.TLabel", background=PAGE_BG, foreground=INK, font=("Segoe UI", 12, "bold"))
        style.configure("Back.TButton", padding=(10, 5))

    def _create_action_button(self, parent, text, command, variant="secondary", state="normal"):
        palette = {
            "primary": ("#2563eb", "#1d4ed8", "#ffffff"),
            "secondary": ("#1f2a44", "#334155", "#e5edf7"),
        }
        bg, hover, fg = palette[variant]
        button = tk.Label(
            parent,
            text=text,
            background=bg,
            foreground=fg,
            font=("Segoe UI", 9, "bold"),
            padx=16,
            pady=9,
            cursor="hand2",
            borderwidth=0,
            state=state,
        )

        def invoke(_event=None):
            if str(button.cget("state")) != "disabled":
                command()

        def enter(_event=None):
            if str(button.cget("state")) != "disabled":
                button.configure(background=hover)

        def leave(_event=None):
            if str(button.cget("state")) != "disabled":
                button.configure(background=bg)

        button.bind("<Button-1>", invoke)
        button.bind("<Enter>", enter)
        button.bind("<Leave>", leave)
        if state == "disabled":
            button.configure(background="#334155", foreground="#7d8ca3", cursor="arrow")
        button.default_bg = bg
        button.default_fg = fg
        button.hover_bg = hover
        return button

    def _create_nav_button(self, parent, text, command):
        button = tk.Label(
            parent,
            text=text,
            background="#17213a",
            foreground="#cbd5e1",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8,
            cursor="hand2",
        )
        button.bind("<Button-1>", lambda _event: command())
        button.bind("<Enter>", lambda _event: button.configure(background="#24324f"))
        button.bind("<Leave>", lambda _event: self._refresh_nav_buttons())
        return button

    def _set_action_button_state(self, button, state):
        button.configure(state=state)
        if state == "disabled":
            button.configure(background="#334155", foreground="#7d8ca3", cursor="arrow")
        else:
            button.configure(background=button.default_bg, foreground=button.default_fg, cursor="hand2")

    def _refresh_nav_buttons(self):
        active_bg = "#2563eb"
        idle_bg = "#17213a"
        hover_fg = "#ffffff"
        idle_fg = "#cbd5e1"
        self.evidence_btn.configure(
            background=active_bg if getattr(self, "active_view", "results") == "results" else idle_bg,
            foreground=hover_fg if getattr(self, "active_view", "results") == "results" else idle_fg,
        )
        self.log_btn.configure(
            background=active_bg if getattr(self, "active_view", "results") == "log" else idle_bg,
            foreground=hover_fg if getattr(self, "active_view", "results") == "log" else idle_fg,
        )

    def _build_evidence_viewer(self):
        self.dashboard_frame = ttk.Frame(self.results_frame, style="App.TFrame")
        self.detail_frame = ttk.Frame(self.results_frame, style="App.TFrame")
        self.detail_pages = {}

        self._build_dashboard()
        self._build_detail_pages()
        self.show_dashboard()

    def _build_dashboard(self):
        header = ttk.Frame(self.dashboard_frame, padding=(4, 6, 4, 18), style="App.TFrame")
        header.pack(fill=tk.X)

        ttk.Label(header, text="Evidence Dashboard", style="DashboardTitle.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Choose a registry evidence category to inspect parsed forensic artifacts.",
            style="Muted.TLabel",
        ).pack(anchor=tk.W, pady=(4, 0))

        self.card_grid = ttk.Frame(self.dashboard_frame, style="App.TFrame")
        self.card_grid.pack(fill=tk.BOTH, expand=True)
        for column in range(3):
            self.card_grid.columnconfigure(column, weight=1, uniform="cards")

        for index, item in enumerate(RESULT_TABS):
            title, _folder, filename, description, badge, color = item
            row = index // 3
            column = index % 3
            self.card_grid.rowconfigure(row, weight=1, uniform="cards")

            outer = tk.Frame(
                self.card_grid,
                background=CARD_SHADOW,
                highlightthickness=1,
                highlightbackground=CARD_SHADOW,
                cursor="hand2",
            )
            outer.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
            outer.columnconfigure(1, weight=1)
            outer.rowconfigure(0, weight=1)

            accent = tk.Frame(outer, width=8, background=color)
            accent.grid(row=0, column=0, sticky="ns")

            content = tk.Frame(outer, background=PANEL_BG, padx=18, pady=18)
            content.grid(row=0, column=1, sticky="nsew")
            content.columnconfigure(0, weight=1)

            badge_label = tk.Label(
                content,
                text=badge,
                background=color,
                foreground="#ffffff",
                font=("Segoe UI", 8, "bold"),
                padx=10,
                pady=4,
            )
            badge_label.grid(row=0, column=0, sticky="w")

            title_label = tk.Label(
                content,
                text=title,
                background=PANEL_BG,
                foreground=INK,
                font=("Segoe UI", 15, "bold"),
                anchor="w",
            )
            title_label.grid(row=1, column=0, sticky="ew", pady=(12, 4))

            description_label = tk.Label(
                content,
                text=description,
                background=PANEL_BG,
                foreground="#475569",
                font=("Segoe UI", 9),
                anchor="nw",
                justify=tk.LEFT,
                wraplength=280,
            )
            description_label.grid(row=2, column=0, sticky="ew")

            item_text = "  ".join(CATEGORY_ITEMS.get(title, ()))
            items_label = tk.Label(
                content,
                text=item_text,
                background=PANEL_BG,
                foreground=color,
                font=("Segoe UI", 9, "bold"),
                anchor="nw",
                justify=tk.LEFT,
                wraplength=290,
            )
            items_label.grid(row=3, column=0, sticky="ew", pady=(12, 0))

            meta_label = tk.Label(
                content,
                text=f"No output loaded | {filename}",
                background=PANEL_BG,
                foreground=MUTED,
                font=("Segoe UI", 9),
                anchor="w",
            )
            meta_label.grid(row=4, column=0, sticky="ew", pady=(14, 0))

            self._bind_card_click(outer, title)
            self._bind_card_hover(outer, content, accent, color)
            self.category_cards[title] = {"frame": outer, "content": content, "accent": accent, "meta": meta_label}

    def _bind_card_click(self, widget, title):
        widget.bind("<Button-1>", lambda _event, tab_title=title: self.show_detail(tab_title))
        for child in widget.winfo_children():
            self._bind_card_click(child, title)

    def _bind_card_hover(self, outer, content, accent, color):
        def enter(_event=None):
            outer.configure(background="#aebed3", highlightbackground="#9fb2cd")
            content.configure(background=CARD_HOVER)
            accent.configure(width=11)
            self._set_child_background(content, CARD_HOVER)

        def leave(_event=None):
            outer.configure(background=CARD_SHADOW, highlightbackground=CARD_SHADOW)
            content.configure(background=PANEL_BG)
            accent.configure(width=8)
            self._set_child_background(content, PANEL_BG)

        for widget in (outer, content, accent, *content.winfo_children()):
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

    def _set_child_background(self, parent, color):
        for child in parent.winfo_children():
            try:
                if str(child.cget("foreground")).lower() == "#ffffff":
                    continue
                child.configure(background=color)
            except tk.TclError:
                pass

    def _build_detail_pages(self):
        for title, folder, filename, description, badge, color in RESULT_TABS:
            page = ttk.Frame(self.detail_frame, style="App.TFrame")
            self.detail_pages[title] = page

            top_bar = ttk.Frame(page, padding=(0, 4, 0, 14), style="App.TFrame")
            top_bar.pack(fill=tk.X)

            self._create_action_button(top_bar, "< Categories", self.show_dashboard, variant="secondary").pack(side=tk.LEFT)

            report_header = tk.Frame(page, background=PANEL_BG, highlightthickness=1, highlightbackground=BORDER, padx=20, pady=18)
            report_header.pack(fill=tk.X)
            report_header.columnconfigure(0, weight=1)

            heading = tk.Frame(report_header, background=PANEL_BG)
            heading.grid(row=0, column=0, sticky="ew")
            heading.columnconfigure(0, weight=1)

            tk.Label(
                heading,
                text=badge,
                background=color,
                foreground="#ffffff",
                font=("Segoe UI", 8, "bold"),
                padx=10,
                pady=4,
            ).grid(row=0, column=0, sticky=tk.W)
            tk.Label(
                heading,
                text=title,
                background=PANEL_BG,
                foreground=INK,
                font=("Segoe UI", 20, "bold"),
            ).grid(row=1, column=0, sticky=tk.W, pady=(10, 2))
            tk.Label(
                heading,
                text=description,
                background=PANEL_BG,
                foreground=MUTED,
                font=("Segoe UI", 10),
            ).grid(row=2, column=0, sticky=tk.W)

            meta = tk.Frame(report_header, background=PANEL_BG)
            meta.grid(row=0, column=1, sticky=tk.E, padx=(18, 0))

            case_path = tk.Label(meta, text="No output loaded", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 8))
            case_path.grid(row=0, column=0, columnspan=2, sticky=tk.E, pady=(0, 8))
            tk.Label(meta, text="Source", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 8, "bold")).grid(
                row=1, column=0, sticky=tk.E, padx=(0, 8)
            )
            tk.Label(meta, text=folder, background=PANEL_BG, foreground=INK, font=("Segoe UI", 9, "bold")).grid(
                row=1, column=1, sticky=tk.W
            )
            tk.Label(meta, text="CSV", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 8, "bold")).grid(
                row=2, column=0, sticky=tk.E, padx=(0, 8), pady=(5, 0)
            )
            tk.Label(meta, text=filename, background=PANEL_BG, foreground=INK, font=("Segoe UI", 9, "bold")).grid(
                row=2, column=1, sticky=tk.W, pady=(5, 0)
            )
            tk.Label(meta, text="Rows", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 8, "bold")).grid(
                row=3, column=0, sticky=tk.E, padx=(0, 8), pady=(5, 0)
            )
            row_count_label = tk.Label(meta, text="0", background=PANEL_BG, foreground=color, font=("Segoe UI", 10, "bold"))
            row_count_label.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))

            status = ttk.Label(page, text="No output loaded", style="Muted.TLabel")
            status.pack(anchor=tk.W, pady=(12, 6))

            filter_bar = tk.Frame(page, background=TEXT_BG, highlightthickness=1, highlightbackground=BORDER, padx=12, pady=10)
            filter_bar.pack(fill=tk.X, pady=(0, 8))
            tk.Label(filter_bar, text="Search", background=TEXT_BG, foreground=INK, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
            search_var = tk.StringVar()
            search_entry = ttk.Entry(filter_bar, textvariable=search_var)
            search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
            clear_btn = self._create_action_button(filter_bar, "Clear", lambda: None, variant="secondary")
            clear_btn.pack(side=tk.RIGHT)

            table_frame = ttk.Frame(page, style="App.TFrame")
            table_frame.pack(fill=tk.BOTH, expand=True)

            tree = ttk.Treeview(table_frame, show="headings")
            y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
            x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
            tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

            tree.grid(row=0, column=0, sticky="nsew")
            y_scroll.grid(row=0, column=1, sticky="ns")
            x_scroll.grid(row=1, column=0, sticky="ew")
            table_frame.columnconfigure(0, weight=1)
            table_frame.rowconfigure(0, weight=1)

            self.result_tables[title] = {
                "tree": tree,
                "status": status,
                "search_var": search_var,
                "headers": [],
                "rows": [],
                "filename": "",
                "case_path": case_path,
                "row_count": row_count_label,
            }
            search_var.trace_add("write", lambda *_args, tab_title=title: self._apply_filter(tab_title))
            clear_btn.bind(
                "<Button-1>",
                lambda _event, tab_title=title: self.result_tables[tab_title]["search_var"].set(""),
            )

    def show_dashboard(self):
        self.detail_frame.pack_forget()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

    def show_detail(self, title):
        self.dashboard_frame.pack_forget()
        for page in self.detail_pages.values():
            page.pack_forget()
        self.detail_frame.pack(fill=tk.BOTH, expand=True)
        self.detail_pages[title].pack(fill=tk.BOTH, expand=True)

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
                self.output_label.config(text=f"Output Folder: {output_path}")
                self.load_output(output_path)
                self.show_results()

        self.root.after(0, update_ui)

    def start_process(self):
        self._set_action_button_state(self.start_btn, "disabled")
        self._set_action_button_state(self.report_btn, "disabled")
        self.output_label.config(text="Output Folder: Running...")
        self.show_log()
        thread = threading.Thread(target=run_forensics, args=(self.log, self.done), daemon=True)
        thread.start()

    def load_latest_output(self, silent=False):
        output_root = Path("output")
        cases = sorted(
            [path for path in output_root.glob("CASE_*") if path.is_dir()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not cases:
            if not silent:
                messagebox.showinfo("No output found", "No CASE_* folders were found under output.")
            return
        self.load_output(cases[0].resolve())

    def load_output(self, output_path):
        output_path = Path(output_path)
        self.current_output_path = output_path
        self._set_action_button_state(self.report_btn, "normal")
        self.output_label.config(text=f"Output Folder: {output_path}")

        for title, folder, filename, _description, _badge, _color in RESULT_TABS:
            csv_path = output_path / folder / filename
            widgets = self.result_tables[title]
            tree = widgets["tree"]
            status = widgets["status"]

            self._clear_tree(tree)
            widgets["headers"] = []
            widgets["rows"] = []
            widgets["filename"] = filename
            widgets["case_path"].config(text=str(output_path))
            widgets["row_count"].config(text="0")
            if not csv_path.exists():
                status.config(text=f"Missing file: {csv_path.name}")
                self._update_category_card(title, "Missing file", filename)
                continue

            try:
                row_count = self._load_csv_into_tree(title, csv_path)
                status.config(text=f"{row_count} rows loaded from {csv_path.name}")
                widgets["row_count"].config(text=str(row_count))
                self._update_category_card(title, f"{row_count} rows loaded", filename)
            except Exception as exc:
                status.config(text=f"Could not load {csv_path.name}: {exc}")
                self._update_category_card(title, "Could not load file", filename)

    def _clear_tree(self, tree):
        tree.delete(*tree.get_children())
        tree["columns"] = ()

    def _load_csv_into_tree(self, title, csv_path):
        widgets = self.result_tables[title]
        tree = widgets["tree"]
        with open(csv_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            headers = next(reader, [])
            if not headers:
                return 0

            rows = [row + [""] * (len(headers) - len(row)) for row in reader]
            rows = [row[: len(headers)] for row in rows]
            widgets["headers"] = headers
            widgets["rows"] = rows

            tree["columns"] = headers
            for header in headers:
                tree.heading(header, text=header.replace("_", " ").title())
                tree.column(header, width=max(130, min(300, len(header) * 14)), anchor=tk.W, stretch=True)

            self._populate_tree(tree, rows)
            return len(rows)

    def _update_category_card(self, title, status, filename):
        card = self.category_cards.get(title)
        if card:
            card["meta"].config(text=f"{status} | {filename}")

    def _apply_filter(self, title):
        widgets = self.result_tables[title]
        tree = widgets["tree"]
        query = widgets["search_var"].get().strip().lower()
        rows = widgets["rows"]
        if query:
            rows = [row for row in rows if query in " ".join(str(value).lower() for value in row)]
        self._populate_tree(tree, rows)
        total = len(widgets["rows"])
        shown = len(rows)
        widgets["status"].config(text=f"{shown} of {total} rows shown")

    def _populate_tree(self, tree, rows):
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", tk.END, values=row)

    def create_report(self):
        if not self.current_output_path:
            messagebox.showinfo("No output loaded", "Load or create an output case before generating a report.")
            return

        selected_formats = [key for key, var in self.report_format_vars.items() if var.get()]
        if not selected_formats:
            messagebox.showinfo("No format selected", "Choose at least one report format: PDF, DOCX, or Excel.")
            return

        self._set_action_button_state(self.report_btn, "disabled")
        self.report_status.config(text=f"Creating {', '.join(fmt.upper() for fmt in selected_formats)}...")
        self.report_progress.pack(side=tk.RIGHT, padx=(0, 10))
        self.report_progress.start(12)
        thread = threading.Thread(
            target=self._create_report_worker,
            args=(self.current_output_path, selected_formats),
            daemon=True,
        )
        thread.start()

    def _create_report_worker(self, output_path, selected_formats):
        try:
            outputs = generate_reports(output_path, formats=selected_formats)
        except Exception as exc:
            self.root.after(0, lambda: self._finish_report_generation(error=exc))
            return

        self.root.after(0, lambda: self._finish_report_generation(outputs=outputs))

    def _finish_report_generation(self, outputs=None, error=None):
        self.report_progress.stop()
        self.report_progress.pack_forget()
        self._set_action_button_state(self.report_btn, "normal")

        if error:
            self.report_status.config(text="Report failed")
            messagebox.showerror("Report failed", f"Could not create report.\n\n{error}")
            return

        lines = []
        outputs = outputs or {}
        for key in ("pdf", "docx", "xlsx"):
            if key in outputs:
                lines.append(f"{key.upper()}: {outputs[key]}")
                self.log(f"[+] Report created ({key.upper()}): {outputs[key]}")
        self.report_status.config(text="Report ready")
        messagebox.showinfo("Report created", "Reports saved at:\n\n" + "\n".join(lines))


if __name__ == "__main__":
    if not is_admin():
        try:
            relaunch_as_admin(__file__)
        except Exception as exc:
            messagebox.showerror("Administrator required", f"Please run as Administrator.\n\n{exc}")
            sys.exit(1)

    root = tk.Tk()
    ForensicUI(root)
    root.mainloop()
