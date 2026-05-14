import threading
from tkinter import messagebox

from core.report_generator import generate_reports


class ReportMixin:
    def create_report(self):
        if not self.current_output_path:
            messagebox.showinfo("No output loaded", "Load or create an output case before generating a report.")
            return

        selected_formats = [key for key, var in self.report_format_vars.items() if var.get()]
        if not selected_formats:
            messagebox.showinfo("No format selected", "Choose at least one report format: PDF or DOCX.")
            return

        self._set_action_button_state(self.report_btn, "disabled")
        self.report_status.config(text=f"Creating {', '.join(fmt.upper() for fmt in selected_formats)}...")
        self.report_progress.pack(side="right", padx=(0, 10))
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
        for key in ("pdf", "docx"):
            if key in outputs:
                lines.append(f"{key.upper()}: {outputs[key]}")
                self.log(f"[+] Report created ({key.upper()}): {outputs[key]}")
        self.report_status.config(text="Report ready")
        messagebox.showinfo("Report created", "Reports saved at:\n\n" + "\n".join(lines))
