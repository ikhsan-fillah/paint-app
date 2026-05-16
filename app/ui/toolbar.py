"""Ribbon toolbar atas dengan grup: Selection, Tools, Shapes, Transform."""
import tkinter as tk
from app.config import (
    COLOR_BG_DARK, COLOR_TEXT, COLOR_TEXT_MUTED,
    COLOR_ACCENT, COLOR_HOVER, COLOR_ACTIVE, COLOR_DIVIDER,
    TOOL_SELECT, TOOL_PENCIL, TOOL_LINE, TOOL_RECT,
    TOOL_CIRCLE, TOOL_ELLIPSE, TOOL_TRIANGLE, TOOL_POLYGON,
    TOOL_FILL, TOOL_EYEDROPPER, TOOL_ERASER, TOOL_TRANSFORM
)


class Toolbar(tk.Frame):
    def __init__(self, parent, state, on_tool_change, on_transform_action, on_canvas_resize):
        super().__init__(parent, bg=COLOR_BG_DARK, height=72)
        self.pack_propagate(False)
        self.state = state
        self.on_tool_change = on_tool_change
        self.on_transform_action = on_transform_action
        self.on_canvas_resize = on_canvas_resize
        self._btn_map = {}
        self._build()

    # ── Builders ─────────────────────────────────────────────────────
    def _tool_btn(self, parent, icon, label, tool_id):
        f = tk.Frame(parent, bg=COLOR_BG_DARK)
        f.pack(side=tk.LEFT, padx=2)
        btn = tk.Button(
            f, text=icon, bg=COLOR_BG_DARK, fg=COLOR_TEXT,
            font=("Segoe UI", 15), bd=0, width=3, height=1,
            activebackground=COLOR_HOVER, cursor="hand2",
            command=lambda t=tool_id: self._select_tool(t)
        )
        btn.pack()
        tk.Label(f, text=label, bg=COLOR_BG_DARK, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 7)).pack()
        self._btn_map[tool_id] = btn
        return btn

    def _action_btn(self, parent, icon, label, cmd):
        """Tombol aksi biasa — tidak masuk _btn_map, tidak jadi active tool."""
        f = tk.Frame(parent, bg=COLOR_BG_DARK)
        f.pack(side=tk.LEFT, padx=2)
        btn = tk.Button(
            f, text=icon, bg=COLOR_BG_DARK, fg=COLOR_TEXT,
            font=("Segoe UI", 13), bd=0, width=3,
            activebackground=COLOR_HOVER, cursor="hand2",
            command=cmd
        )
        btn.pack()
        tk.Label(f, text=label, bg=COLOR_BG_DARK, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 7)).pack()
        return btn

    def _group(self, label):
        outer = tk.Frame(self, bg=COLOR_BG_DARK)
        outer.pack(side=tk.LEFT, padx=4, fill=tk.Y)
        inner = tk.Frame(outer, bg=COLOR_BG_DARK)
        inner.pack(expand=True)
        tk.Label(outer, text=label, bg=COLOR_BG_DARK, fg=COLOR_TEXT_MUTED,
                 font=("Segoe UI", 8)).pack(side=tk.BOTTOM, pady=2)
        return inner

    def _divider(self):
        tk.Frame(self, bg=COLOR_DIVIDER, width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=8, padx=2)

    def _select_tool(self, tool_id):
        self.state.active_tool = tool_id
        for tid, btn in self._btn_map.items():
            btn.config(bg=COLOR_ACTIVE if tid == tool_id else COLOR_BG_DARK)
        self.on_tool_change(tool_id)

    # ── Build layout ─────────────────────────────────────────────────
    def _build(self):
        # Group: Selection
        g = self._group("Selection")
        self._tool_btn(g, "⬺", "Select",  TOOL_SELECT)
        # Crop — action button, buka dialog resize canvas (bukan tool)
        self._action_btn(g, "✂", "Crop", lambda: self.on_canvas_resize())
        self._divider()

        # Group: Tools
        g = self._group("Tools")
        self._tool_btn(g, "✏", "Pencil",  TOOL_PENCIL)
        self._tool_btn(g, "⌫", "Eraser",  TOOL_ERASER)
        self._tool_btn(g, "🪣", "Fill",   TOOL_FILL)
        self._tool_btn(g, "💉", "Picker", TOOL_EYEDROPPER)
        self._divider()

        # Group: Shapes
        g = self._group("Shapes")
        self._tool_btn(g, "╱",  "Line",     TOOL_LINE)
        self._tool_btn(g, "○",  "Circle",   TOOL_CIRCLE)
        self._tool_btn(g, "⬭",  "Ellipse",  TOOL_ELLIPSE)
        self._tool_btn(g, "□",  "Rect",     TOOL_RECT)
        self._tool_btn(g, "△",  "Triangle", TOOL_TRIANGLE)
        self._tool_btn(g, "⬡",  "Polygon",  TOOL_POLYGON)
        self._divider()

        # Group: Transform
        g = self._group("Transform")
        self._action_btn(g, "↔", "Translasi",
            lambda: self.on_transform_action("translate"))
        self._action_btn(g, "↻", "Rotasi",
            lambda: self.on_transform_action("rotate"))
        self._action_btn(g, "⤢", "Skala",
            lambda: self.on_transform_action("scale"))
        self._action_btn(g, "⇔", "Refleksi",
            lambda: self.on_transform_action("reflect"))
        self._action_btn(g, "⤡", "Shear",
            lambda: self.on_transform_action("shear"))
        self._divider()

    def set_active(self, tool_id):
        self._select_tool(tool_id)
