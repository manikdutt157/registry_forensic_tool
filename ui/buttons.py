import tkinter as tk


class ButtonMixin:
    def _create_action_button(self, parent, text, command, variant="secondary", state="normal"):
        palette = {
            "primary": ("#1d4ed8", "#1e40af", "#ffffff"),
            "secondary": ("#374151", "#4b5563", "#f9fafb"),
        }
        bg, hover, fg = palette[variant]
        button = tk.Label(
            parent,
            text=text,
            background=bg,
            foreground=fg,
            font=("Segoe UI", 12, "bold"),
            padx=20,
            pady=12,
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
            background="#1f2937",
            foreground="#f3f4f6",
            font=("Segoe UI", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
        )
        button.bind("<Button-1>", lambda _event: command())
        button.bind("<Enter>", lambda _event: button.configure(background="#374151"))
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
        idle_bg = "#1f2937"
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
