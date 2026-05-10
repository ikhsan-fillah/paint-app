"""Panel warna: swatch aktif fg/bg + palette grid + color wheel button."""
import tkinter as tk
from tkinter import colorchooser
from app.config import COLOR_BG_DARK, COLOR_PALETTE, COLOR_ACCENT, COLOR_DIVIDER


class ColorPalette(tk.Frame):
    def __init__(self, parent, state, on_color_change):
        super().__init__(parent, bg=COLOR_BG_DARK)
        self.state = state
        self.on_color_change = on_color_change
        self._build()

    def _build(self):
        # Swatch fg/bg
        swatch_frame = tk.Frame(self, bg=COLOR_BG_DARK)
        swatch_frame.pack(side=tk.LEFT, padx=8)

        # bg swatch (di belakang)
        self._bg_swatch = tk.Canvas(
            swatch_frame, width=22, height=22, bg=self.state.bg_color,
            highlightthickness=1, highlightbackground="#666", cursor="hand2"
        )
        self._bg_swatch.place(x=10, y=10)
        self._bg_swatch.bind("<Button-1>", lambda e: self._pick_color("bg"))

        # fg swatch (di depan)
        self._fg_swatch = tk.Canvas(
            swatch_frame, width=24, height=24, bg=self.state.fg_color,
            highlightthickness=1, highlightbackground="#aaa", cursor="hand2"
        )
        self._fg_swatch.place(x=0, y=0)
        self._fg_swatch.bind("<Button-1>", lambda e: self._pick_color("fg"))

        # Spacer supaya swatch_frame punya ukuran
        tk.Frame(swatch_frame, width=38, height=36, bg=COLOR_BG_DARK).pack()

        # Divider
        tk.Frame(self, bg=COLOR_DIVIDER, width=1).pack(side=tk.LEFT, fill=tk.Y, pady=4)

        # Grid palette
        palette_frame = tk.Frame(self, bg=COLOR_BG_DARK)
        palette_frame.pack(side=tk.LEFT, padx=6)

        cols = 10
        for i, color in enumerate(COLOR_PALETTE):
            row, col = divmod(i, cols)
            btn = tk.Canvas(
                palette_frame, width=16, height=16, bg=color,
                highlightthickness=1, highlightbackground="#444",
                cursor="hand2"
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
            btn.bind("<Button-1>", lambda e, c=color: self._set_fg(c))
            btn.bind("<Button-3>", lambda e, c=color: self._set_bg(c))

        # Color wheel button
        tk.Button(
            self, text="🎨", bg=COLOR_BG_DARK, fg="white",
            font=("Segoe UI", 14), bd=0, cursor="hand2",
            activebackground="#333",
            command=lambda: self._pick_color("fg")
        ).pack(side=tk.LEFT, padx=6)

    def _set_fg(self, color):
        self.state.fg_color = color
        self._fg_swatch.config(bg=color)
        self.on_color_change("fg", color)

    def _set_bg(self, color):
        self.state.bg_color = color
        self._bg_swatch.config(bg=color)
        self.on_color_change("bg", color)

    def _pick_color(self, target):
        init = self.state.fg_color if target == "fg" else self.state.bg_color
        result = colorchooser.askcolor(color=init, title="Pilih Warna")
        if result and result[1]:
            if target == "fg":
                self._set_fg(result[1])
            else:
                self._set_bg(result[1])

    def refresh(self):
        self._fg_swatch.config(bg=self.state.fg_color)
        self._bg_swatch.config(bg=self.state.bg_color)
