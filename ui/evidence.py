import csv
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from core.utils import DEFAULT_OUTPUT_ROOT
from ui.constants import (
    BORDER,
    CARD_HOVER,
    CARD_SHADOW,
    CATEGORY_ITEMS,
    INK,
    MUTED,
    PAGE_BG,
    PANEL_BG,
    RESULT_TABS,
    TEXT_BG,
)


class EvidenceViewMixin:
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
                font=("Segoe UI", 10, "bold"),
                padx=10,
                pady=4,
            )
            badge_label.grid(row=0, column=0, sticky="w")

            title_label = tk.Label(
                content,
                text=title,
                background=PANEL_BG,
                foreground=INK,
                font=("Segoe UI", 19, "bold"),
                anchor="w",
            )
            title_label.grid(row=1, column=0, sticky="ew", pady=(12, 4))

            description_label = tk.Label(
                content,
                text=description,
                background=PANEL_BG,
                foreground="#374151",
                font=("Segoe UI", 12),
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
                font=("Segoe UI", 12, "bold"),
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
                font=("Segoe UI", 12),
                anchor="w",
            )
            meta_label.grid(row=4, column=0, sticky="ew", pady=(14, 0))

            self._bind_card_click(outer, title)
            self._bind_card_hover(outer, content, accent)
            self.category_cards[title] = {"frame": outer, "content": content, "accent": accent, "meta": meta_label}

    def _bind_card_click(self, widget, title):
        widget.bind("<Button-1>", lambda _event, tab_title=title: self.show_detail(tab_title))
        for child in widget.winfo_children():
            self._bind_card_click(child, title)

    def _bind_card_hover(self, outer, content, accent):
        def enter(_event=None):
            outer.configure(background="#94a3b8", highlightbackground="#64748b")
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

            tk.Label(heading, text=badge, background=color, foreground="#ffffff", font=("Segoe UI", 10, "bold"), padx=10, pady=4).grid(
                row=0, column=0, sticky=tk.W
            )
            tk.Label(heading, text=title, background=PANEL_BG, foreground=INK, font=("Segoe UI", 24, "bold")).grid(
                row=1, column=0, sticky=tk.W, pady=(10, 2)
            )
            tk.Label(heading, text=description, background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 12)).grid(
                row=2, column=0, sticky=tk.W
            )

            meta = tk.Frame(report_header, background=PANEL_BG)
            meta.grid(row=0, column=1, sticky=tk.E, padx=(18, 0))

            case_path = tk.Label(meta, text="No output loaded", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 10))
            case_path.grid(row=0, column=0, columnspan=2, sticky=tk.E, pady=(0, 8))
            tk.Label(meta, text="Source", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 10, "bold")).grid(
                row=1, column=0, sticky=tk.E, padx=(0, 8)
            )
            tk.Label(meta, text=folder, background=PANEL_BG, foreground=INK, font=("Segoe UI", 11, "bold")).grid(
                row=1, column=1, sticky=tk.W
            )
            tk.Label(meta, text="CSV", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 10, "bold")).grid(
                row=2, column=0, sticky=tk.E, padx=(0, 8), pady=(5, 0)
            )
            tk.Label(meta, text=filename, background=PANEL_BG, foreground=INK, font=("Segoe UI", 11, "bold")).grid(
                row=2, column=1, sticky=tk.W, pady=(5, 0)
            )
            tk.Label(meta, text="Rows", background=PANEL_BG, foreground=MUTED, font=("Segoe UI", 10, "bold")).grid(
                row=3, column=0, sticky=tk.E, padx=(0, 8), pady=(5, 0)
            )
            row_count_label = tk.Label(meta, text="0", background=PANEL_BG, foreground=color, font=("Segoe UI", 12, "bold"))
            row_count_label.grid(row=3, column=1, sticky=tk.W, pady=(5, 0))

            status = ttk.Label(page, text="No output loaded", style="Muted.TLabel")
            status.pack(anchor=tk.W, pady=(12, 6))

            filter_bar = tk.Frame(page, background=TEXT_BG, highlightthickness=1, highlightbackground=BORDER, padx=12, pady=10)
            filter_bar.pack(fill=tk.X, pady=(0, 8))
            tk.Label(filter_bar, text="Search", background=TEXT_BG, foreground=INK, font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
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
            clear_btn.bind("<Button-1>", lambda _event, tab_title=title: self.result_tables[tab_title]["search_var"].set(""))

    def show_dashboard(self):
        self.detail_frame.pack_forget()
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)

    def show_detail(self, title):
        self.dashboard_frame.pack_forget()
        for page in self.detail_pages.values():
            page.pack_forget()
        self.detail_frame.pack(fill=tk.BOTH, expand=True)
        self.detail_pages[title].pack(fill=tk.BOTH, expand=True)

    def load_latest_output(self, silent=False):
        output_root = DEFAULT_OUTPUT_ROOT
        cases = sorted(
            [path for path in output_root.glob("CASE_*") if path.is_dir()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if not cases:
            if not silent:
                messagebox.showinfo("No case found", f"No CASE_* folders were found under {output_root}.")
            return
        self.load_output(cases[0].resolve())

    def load_output(self, output_path):
        output_path = Path(output_path)
        self.current_output_path = output_path
        self._set_action_button_state(self.report_btn, "normal")
        self.output_label.config(text=f"Case Folder: {output_path}")

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
                tree.column(header, width=max(190, min(420, len(header) * 18)), anchor=tk.W, stretch=True)

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
