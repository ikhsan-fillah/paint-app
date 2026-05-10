"""Status bar bawah: koordinat kursor, dimensi canvas, zoom."""
import tkinter as tk
from app.config import COLOR_BG_STATUS, COLOR_TEXT, COLOR_TEXT_MUTED, COLOR_ACCENT, ZOOM_MIN, ZOOM_MAX


class StatusBar(tk.Frame):
    def __init__(self, parent, state, on_zoom_change):
        super().__init__(parent, bg=COLOR_BG_STATUS, height=28)
        self.state = state
        self.on_zoom_change = on_zoom_change
        self._build()

    def _build(self):
        # Koordinat kursor
        self._lbl_cursor = tk.Label(
            self, text="X: 0, Y: 0",
            bg=COLOR_BG_STATUS, fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9), padx=12
        )
        self._lbl_cursor.pack(side=tk.LEFT)

        self._sep()

        # Dimensi canvas
        self._lbl_size = tk.Label(
            self, text="800 × 600 px",
            bg=COLOR_BG_STATUS, fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9), padx=12
        )
        self._lbl_size.pack(side=tk.LEFT)

        # Zoom controls — sebelah kanan
        zoom_frame = tk.Frame(self, bg=COLOR_BG_STATUS)
        zoom_frame.pack(side=tk.RIGHT, padx=12)

        tk.Button(
            zoom_frame, text="−", bg=COLOR_BG_STATUS, fg=COLOR_TEXT,
            font=("Segoe UI", 10, "bold"), bd=0, activebackground="#333",
            command=self._zoom_out, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        self._zoom_var = tk.IntVar(value=100)
        self._zoom_slider = tk.Scale(
            zoom_frame, from_=ZOOM_MIN, to=ZOOM_MAX,
            orient=tk.HORIZONTAL, variable=self._zoom_var,
            bg=COLOR_BG_STATUS, fg=COLOR_TEXT,
            troughcolor="#444", highlightthickness=0,
            showvalue=False, length=120, sliderlength=14,
            command=self._on_slider
        )
        self._zoom_slider.pack(side=tk.LEFT)

        tk.Button(
            zoom_frame, text="+", bg=COLOR_BG_STATUS, fg=COLOR_TEXT,
            font=("Segoe UI", 10, "bold"), bd=0, activebackground="#333",
            command=self._zoom_in, cursor="hand2"
        ).pack(side=tk.LEFT, padx=2)

        self._lbl_zoom = tk.Label(
            zoom_frame, text="100%",
            bg=COLOR_BG_STATUS, fg=COLOR_TEXT,
            font=("Segoe UI", 9), width=5
        )
        self._lbl_zoom.pack(side=tk.LEFT, padx=4)

    def _sep(self):
        tk.Frame(self, bg="#3a3a3a", width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4)

    def _on_slider(self, val):
        pct = int(float(val))
        self._lbl_zoom.config(text=f"{pct}%")
        self.on_zoom_change(pct)

    def _zoom_in(self):
        v = min(self._zoom_var.get() + 10, ZOOM_MAX)
        self._zoom_var.set(v)
        self._on_slider(v)

    def _zoom_out(self):
        v = max(self._zoom_var.get() - 10, ZOOM_MIN)
        self._zoom_var.set(v)
        self._on_slider(v)

    def update_cursor(self, x, y):
        self._lbl_cursor.config(text=f"X: {x},  Y: {y}")

    def update_size(self, w, h):
        self._lbl_size.config(text=f"{w} × {h} px")

    def update_zoom(self, pct):
        self._zoom_var.set(pct)
        self._lbl_zoom.config(text=f"{pct}%")
