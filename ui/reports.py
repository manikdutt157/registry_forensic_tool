import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from core.report_generator import generate_reports


class ReportMixin:
    def create_report(self):
        if not self.current_output_path:
            messagebox.showinfo("No case loaded", "Load or create a case before generating a report.")
            return

        selected_formats = [key for key, var in self.report_format_vars.items() if var.get()]
        if not selected_formats:
            messagebox.showinfo(
                "No format selected", "Choose at least one report format: PDF, DOCX, or HTML."
            )
            return

        report_details = self._prompt_report_details()
        if report_details is None:
            return

        self._set_action_button_state(self.report_btn, "disabled")
        self.report_status.config(text=f"Creating {', '.join(fmt.upper() for fmt in selected_formats)}...")
        self.report_progress.pack(side="right", padx=(0, 10))
        self.report_progress.start(12)
        thread = threading.Thread(
            target=self._create_report_worker,
            args=(self.current_output_path, selected_formats, report_details),
            daemon=True,
        )
        thread.start()

    def _prompt_report_details(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Report Details")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=18)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Enter Report Details", font=("Segoe UI", 14, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 12)
        )

        fields = [
            ("Case Name", getattr(self.current_output_path, "name", "")),
            ("Case Number", ""),
            ("Investigator Name", ""),
            ("Organization", ""),
            ("Evidence ID", ""),
            ("Subject", ""),
            ("Examination Date", datetime.now().strftime("%Y-%m-%d")),
            ("Notes", ""),
        ]
        entries = {}
        for row, (label, default) in enumerate(fields, start=1):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky=tk.W, padx=(0, 12), pady=5)
            entry = ttk.Entry(frame, width=44)
            entry.insert(0, default)
            entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
            entries[label] = entry

        result = {"details": None}

        def save():
            result["details"] = {label: entry.get().strip() for label, entry in entries.items()}
            dialog.destroy()

        def cancel():
            dialog.destroy()

        buttons = ttk.Frame(frame)
        buttons.grid(row=len(fields) + 1, column=0, columnspan=2, sticky=tk.E, pady=(14, 0))
        ttk.Button(buttons, text="Cancel", command=cancel).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(buttons, text="Create Report", command=save).pack(side=tk.RIGHT)

        entries["Case Name"].focus_set()
        dialog.bind("<Return>", lambda _event: save())
        dialog.bind("<Escape>", lambda _event: cancel())
        self.root.wait_window(dialog)
        return result["details"]

    def _create_report_worker(self, output_path, selected_formats, report_details):
        try:
            outputs = generate_reports(output_path, formats=selected_formats, report_details=report_details)
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
        for key in ("pdf", "docx", "html"):
            if key in outputs:
                lines.append(f"{key.upper()}: {outputs[key]}")
                self.log(f"[+] Report created ({key.upper()}): {outputs[key]}")
        self.report_status.config(text="Report ready")
        messagebox.showinfo("Report created", "Reports saved at:\n\n" + "\n".join(lines))
