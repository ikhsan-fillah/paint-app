"""Sub-bar properties: line style, fill toggle."""
import tkinter as tk
from tkinter import ttk
from app.config import COLOR_BG_PANEL, COLOR_TEXT, COLOR_TEXT_MUTED, LINE_STYLES


class PropertiesBar(tk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, bg=COLOR_BG_PANEL, height=30)
        self.state = state
        self._build()

    def _build(self):
        style = ttk.Style()
        style.configure("Prop.TCombobox", fieldbackground="#333", background="#333",
                        foreground=COLOR_TEXT, selectbackground="#444")

        tk.Label(self, text="Line Style:", bg=COLOR_BG_PANEL,
                 fg=COLOR_TEXT_MUTED, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(12,4))

        self._style_var = tk.StringVar(value="Solid")
        cb = ttk.Combobox(
            self, textvariable=self._style_var,
            values=list(LINE_STYLES.keys()),
            state="readonly", width=10,
            style="Prop.TCombobox"
        )
        cb.pack(side=tk.LEFT, padx=4)
        cb.bind("<<ComboboxSelected>>", self._on_style_change)

        tk.Frame(self, bg="#3a3a3a", width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4, padx=8)

        self._fill_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self, text="Fill", variable=self._fill_var,
            bg=COLOR_BG_PANEL, fg=COLOR_TEXT,
            selectcolor="#444", activebackground=COLOR_BG_PANEL,
            font=("Segoe UI", 9),
            command=self._on_fill_change
        ).pack(side=tk.LEFT, padx=4)

    def _on_style_change(self, event=None):
        self.state.line_style = self._style_var.get()

    def _on_fill_change(self):
        self.state.fill_shape = self._fill_var.get()
