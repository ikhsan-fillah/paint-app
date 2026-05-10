"""Panel kiri vertikal: slider Line Width dan Opacity."""
import tkinter as tk
from app.config import COLOR_BG_DARK, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_ACCENT


class SidePanel(tk.Frame):
    def __init__(self, parent, state):
        super().__init__(parent, bg=COLOR_BG_DARK, width=48)
        self.state = state
        self.pack_propagate(False)
        self._build()

    def _build(self):
        # ── Line Width ────────────────────────────────
        width_frame = tk.Frame(self, bg=COLOR_BG_DARK)
        width_frame.pack(fill=tk.X, pady=(16, 0))

        # Icon garis bertumpuk
        tk.Label(
            width_frame, text="≡", bg=COLOR_BG_DARK, fg=COLOR_TEXT,
            font=("Segoe UI", 14)
        ).pack()

        self._width_var = tk.IntVar(value=self.state.line_width)
        tk.Scale(
            width_frame, from_=20, to=1,
            orient=tk.VERTICAL, variable=self._width_var,
            bg=COLOR_BG_DARK, fg=COLOR_TEXT,
            troughcolor="#444", highlightthickness=0,
            showvalue=False, length=100, sliderlength=14,
            command=self._on_width
        ).pack(padx=10)

        self._lbl_width = tk.Label(
            width_frame, text=f"{self.state.line_width}px",
            bg=COLOR_BG_DARK, fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 8)
        )
        self._lbl_width.pack()

        # Divider
        tk.Frame(self, bg="#3a3a3a", height=1).pack(fill=tk.X, padx=4, pady=8)

        # ── Opacity ───────────────────────────────────
        opacity_frame = tk.Frame(self, bg=COLOR_BG_DARK)
        opacity_frame.pack(fill=tk.X)

        tk.Label(
            opacity_frame, text="💧", bg=COLOR_BG_DARK,
            font=("Segoe UI", 12)
        ).pack()

        self._opacity_var = tk.IntVar(value=self.state.opacity)
        self._opacity_slider = tk.Scale(
            opacity_frame, from_=100, to=0,
            orient=tk.VERTICAL, variable=self._opacity_var,
            bg=COLOR_BG_DARK, fg=COLOR_ACCENT,
            troughcolor=COLOR_ACCENT, highlightthickness=0,
            showvalue=False, length=100, sliderlength=14,
            command=self._on_opacity
        )
        self._opacity_slider.pack(padx=10)

        self._lbl_opacity = tk.Label(
            opacity_frame, text="100%",
            bg=COLOR_BG_DARK, fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 8)
        )
        self._lbl_opacity.pack()

    def _on_width(self, val):
        v = int(float(val))
        self.state.line_width = v
        self._lbl_width.config(text=f"{v}px")

    def _on_opacity(self, val):
        v = int(float(val))
        self.state.opacity = v
        self._lbl_opacity.config(text=f"{v}%")
