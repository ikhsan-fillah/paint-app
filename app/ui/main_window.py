"""Jendela utama — merakit semua komponen UI dan tool registry."""
import tkinter as tk
from tkinter import messagebox
from app.config import COLOR_BG_WORKSPACE, COLOR_BG_DARK
from app.core.canvas_state import CanvasState
from app.core.history import History
from app.core.exporter import export_canvas
from app.ui.toolbar import Toolbar
from app.ui.properties_bar import PropertiesBar
from app.ui.side_panel import SidePanel
from app.ui.canvas_widget import CanvasWidget
from app.ui.color_palette import ColorPalette
from app.ui.status_bar import StatusBar
from app.tools.select_tool import SelectTool
from app.tools.pencil_tool import PencilTool
from app.tools.shape_tool import ShapeTool
from app.tools.fill_tool import FillTool
from app.tools.eyedropper_tool import EyedropperTool
from app.tools.transform_tool import TransformTool
from app.config import (
    TOOL_SELECT, TOOL_PENCIL, TOOL_LINE, TOOL_RECT,
    TOOL_CIRCLE, TOOL_ELLIPSE, TOOL_TRIANGLE, TOOL_POLYGON,
    TOOL_FILL, TOOL_EYEDROPPER, TOOL_ERASER, TOOL_TRANSFORM
)


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Paint App — Grafika Komputer")
        self.root.geometry("1280x720")
        self.root.configure(bg=COLOR_BG_DARK)
        self.root.minsize(800, 500)

        self.state   = CanvasState()
        self.history = History()
        self._prev_fg_color = self.state.fg_color  # simpan warna sebelum eraser

        self._build_menu()
        self._build_ui()
        self._register_tools()
        self._bind_shortcuts()

        # Set tool awal
        self.toolbar.set_active(TOOL_LINE)

    # ── Menu bar ─────────────────────────────────────────────────────
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Baru",           command=self._new_canvas)
        file_menu.add_command(label="Simpan (PNG)",   command=self._save)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar",          command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo  Ctrl+Z", command=self._undo)
        edit_menu.add_command(label="Redo  Ctrl+Y", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Hapus Canvas",  command=self._clear)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.root.config(menu=menubar)

    # ── UI layout ────────────────────────────────────────────────────
    def _build_ui(self):
        # Toolbar atas
        self.toolbar = Toolbar(
            self.root, self.state,
            on_tool_change=self._on_tool_change,
            on_transform_action=self._on_transform_action,
            on_canvas_resize=self._on_canvas_resize
        )
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Color palette (masih bagian toolbar row)
        self.color_palette = ColorPalette(
            self.toolbar, self.state,
            on_color_change=self._on_color_change
        )
        self.color_palette.pack(side=tk.RIGHT, padx=8)

        # Properties sub-bar
        self.props_bar = PropertiesBar(self.root, self.state)
        self.props_bar.pack(side=tk.TOP, fill=tk.X)

        # Body (side panel + canvas)
        body = tk.Frame(self.root, bg=COLOR_BG_WORKSPACE)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.side_panel = SidePanel(body, self.state)
        self.side_panel.pack(side=tk.LEFT, fill=tk.Y)

        self._canvas_frame = body

        # Status bar
        self.status_bar = StatusBar(
            self.root, self.state,
            on_zoom_change=self._on_zoom_change
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _register_tools(self):
        self.canvas_widget = CanvasWidget(
            self._canvas_frame, self.state, self.history,
            tool_registry={},
            on_cursor_move=self._on_cursor_move
        )
        self.canvas_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        redraw  = self.canvas_widget.redraw
        canvas  = self.canvas_widget._canvas
        get_base = self.canvas_widget.get_base_image
        set_base = self.canvas_widget.set_base_image
        get_comp = self.canvas_widget.get_composited_image

        shape_tool = ShapeTool(self.state, canvas, redraw, self.canvas_widget._canvas_to_screen)

        self._tools = {
            TOOL_SELECT:     SelectTool(self.state, canvas, redraw),
            TOOL_PENCIL:     PencilTool(self.state, canvas, redraw,
                                        to_screen_fn=self.canvas_widget._canvas_to_screen),
            TOOL_LINE:       shape_tool,
            TOOL_RECT:       shape_tool,
            TOOL_CIRCLE:     shape_tool,
            TOOL_ELLIPSE:    shape_tool,
            TOOL_TRIANGLE:   shape_tool,
            TOOL_POLYGON:    shape_tool,
            TOOL_FILL:       FillTool(self.state, canvas, redraw, get_comp, get_base, set_base),
            TOOL_EYEDROPPER: EyedropperTool(self.state, canvas, redraw, get_comp,
                                             self._on_eyedropper_pick),
            TOOL_ERASER:     PencilTool(
                self.state, canvas, redraw,
                get_base_image_fn=self.canvas_widget.get_base_image,
                set_base_image_fn=self.canvas_widget.set_base_image,
                flatten_fn=self.canvas_widget.flatten_objects_to_base,
                to_screen_fn=self.canvas_widget._canvas_to_screen
            ),
            TOOL_TRANSFORM:  TransformTool(self.state, canvas, redraw),
        }
        self.canvas_widget.tool_registry = self._tools
        self.status_bar.update_size(self.state.width, self.state.height)

    # ── Callbacks ────────────────────────────────────────────────────
    def _on_tool_change(self, tool_id):
        if tool_id == TOOL_ERASER:
            # simpan warna fg sekarang, ganti ke bg untuk eraser
            self._prev_fg_color = self.state.fg_color
            self.state.fg_color = self.state.bg_color
        else:
            # kembalikan warna fg jika sebelumnya pakai eraser
            if self.state.fg_color == self.state.bg_color and self._prev_fg_color:
                self.state.fg_color = self._prev_fg_color
            self.color_palette.refresh()
        self.canvas_widget.redraw()

    def _on_color_change(self, target, color):
        self.canvas_widget.redraw()

    def _on_cursor_move(self, x, y):
        self.state.cursor_x = x
        self.state.cursor_y = y
        self.status_bar.update_cursor(x, y)
        self.status_bar.update_size(self.state.width, self.state.height)

    def _on_zoom_change(self, pct):
        self.canvas_widget.zoom_update(pct)

    def _on_eyedropper_pick(self, color):
        self.color_palette.refresh()

    def _on_canvas_resize(self):
        """Buka dialog untuk mengubah ukuran / rasio canvas."""
        win = tk.Toplevel(self.root)
        win.title("Ubah Ukuran Canvas")
        win.geometry("280x190")
        win.configure(bg=COLOR_BG_DARK)
        win.resizable(False, False)
        win.grab_set()

        fields = [("Lebar (px)", self.state.width), ("Tinggi (px)", self.state.height)]
        entries = []
        for label, default in fields:
            row = tk.Frame(win, bg=COLOR_BG_DARK)
            row.pack(fill=tk.X, padx=20, pady=8)
            tk.Label(row, text=label, bg=COLOR_BG_DARK, fg="white",
                     font=("Segoe UI", 10), width=12, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(row, bg="#333", fg="white", insertbackground="white",
                         font=("Segoe UI", 10), width=8)
            e.insert(0, str(default))
            e.pack(side=tk.LEFT, padx=6)
            entries.append(e)

        # Preset rasio
        preset_frame = tk.Frame(win, bg=COLOR_BG_DARK)
        preset_frame.pack(pady=4)
        tk.Label(preset_frame, text="Preset:", bg=COLOR_BG_DARK, fg="#aaa",
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=4)
        for label, w, h in [("4:3", 800, 600), ("16:9", 1280, 720), ("1:1", 600, 600)]:
            tk.Button(
                preset_frame, text=label, bg="#333", fg="white",
                font=("Segoe UI", 8), bd=0, padx=8, pady=2,
                cursor="hand2", activebackground="#555",
                command=lambda _w=w, _h=h: [
                    entries[0].delete(0, tk.END), entries[0].insert(0, str(_w)),
                    entries[1].delete(0, tk.END), entries[1].insert(0, str(_h))
                ]
            ).pack(side=tk.LEFT, padx=3)

        def apply():
            try:
                new_w = max(100, int(entries[0].get()))
                new_h = max(100, int(entries[1].get()))
            except ValueError:
                messagebox.showerror("Error", "Masukkan angka yang valid.", parent=win)
                return
            self.canvas_widget.resize_canvas(new_w, new_h)
            self.status_bar.update_size(new_w, new_h)
            win.destroy()

        tk.Button(
            win, text="Apply", bg="#00b4d8", fg="white",
            font=("Segoe UI", 10, "bold"), bd=0, padx=20, pady=4,
            cursor="hand2", command=apply
        ).pack(pady=8)

    def _on_transform_action(self, action):
        """Tampilkan dialog input lalu apply transformasi."""
        tool: TransformTool = self._tools.get(TOOL_TRANSFORM)
        if not tool:
            return
        if self.state.selected_index == -1:
            messagebox.showwarning(
                "Transform",
                "Pilih objek dulu menggunakan tool Select Transform (✥)."
            )
            return

        if action == "translate":
            self._translate_dialog(tool)
        elif action == "rotate":
            self._transform_dialog("Rotasi",
                [("Sudut (°)", 45)],
                lambda v: self._apply_transform(lambda: tool.apply_rotate(v[0])))
        elif action == "scale":
            self._transform_dialog("Skala",
                [("sx", 1.5), ("sy", 1.5)],
                lambda v: self._apply_transform(lambda: tool.apply_scale(v[0], v[1])))
        elif action == "reflect":
            self._reflect_dialog(tool)
        elif action == "shear":
            self._transform_dialog("Shear",
                [("shx", 0.0), ("shy", 0.0)],
                lambda v: self._apply_transform(lambda: tool.apply_shear(v[0], v[1])))

    def _apply_transform(self, apply_fn):
        self.history.save(self.state.objects, self.canvas_widget.get_base_image())
        apply_fn()

    def _transform_dialog(self, title, fields, apply_fn):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("260x" + str(100 + len(fields) * 44))
        win.configure(bg=COLOR_BG_DARK)
        win.resizable(False, False)
        win.grab_set()

        entries = []
        for label, default in fields:
            row = tk.Frame(win, bg=COLOR_BG_DARK)
            row.pack(fill=tk.X, padx=16, pady=8)
            tk.Label(row, text=label, bg=COLOR_BG_DARK,
                     fg="white", width=10, anchor="w",
                     font=("Segoe UI", 10)).pack(side=tk.LEFT)
            e = tk.Entry(row, bg="#333", fg="white", insertbackground="white",
                         font=("Segoe UI", 10), width=10)
            e.insert(0, str(default))
            e.pack(side=tk.LEFT, padx=6)
            entries.append(e)

        def ok():
            try:
                vals = [float(e.get()) for e in entries]
                apply_fn(vals)
            except ValueError:
                messagebox.showerror("Error", "Masukkan nilai angka yang valid.", parent=win)
                return
            win.destroy()

        tk.Button(
            win, text="Apply", bg="#00b4d8", fg="white",
            font=("Segoe UI", 10, "bold"), bd=0, padx=16, pady=4,
            cursor="hand2", command=ok
        ).pack(pady=10)

    def _reflect_dialog(self, tool):
        win = tk.Toplevel(self.root)
        win.title("Refleksi")
        win.geometry("220x210")
        win.configure(bg=COLOR_BG_DARK)
        win.resizable(False, False)
        win.grab_set()
        for label, mode in [
            ("Sumbu X", "x"), ("Sumbu Y", "y"),
            ("Titik Pusat", "origin"), ("Diagonal y=x", "diagonal")
        ]:
            tk.Button(
                win, text=label, bg="#333", fg="white",
                font=("Segoe UI", 10), bd=0, padx=12, pady=6,
                activebackground="#00b4d8", cursor="hand2",
                command=lambda m=mode: [self._apply_transform(lambda: tool.apply_reflect(m)), win.destroy()]
            ).pack(fill=tk.X, padx=16, pady=3)

    def _translate_dialog(self, tool):
        win = tk.Toplevel(self.root)
        win.title("Translasi")
        win.geometry("260x240")
        win.configure(bg=COLOR_BG_DARK)
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="Jarak (px)", bg=COLOR_BG_DARK, fg="#ccc",
                 font=("Segoe UI", 9)).pack(pady=(12, 4))

        dist_var = tk.DoubleVar(value=10)
        dist_entry = tk.Entry(win, bg="#333", fg="white", insertbackground="white",
                              font=("Segoe UI", 10), width=10, textvariable=dist_var)
        dist_entry.pack()

        grid = tk.Frame(win, bg=COLOR_BG_DARK)
        grid.pack(pady=12)

        def move(dx, dy):
            try:
                d = float(dist_var.get())
            except ValueError:
                messagebox.showerror("Error", "Masukkan angka yang valid.", parent=win)
                return
            self._apply_transform(lambda: tool.apply_translate(dx * d, dy * d))

        btn_style = dict(bg="#333", fg="white", font=("Segoe UI", 10),
                         bd=0, width=4, height=2, cursor="hand2",
                         activebackground="#00b4d8")

        tk.Button(grid, text="↖", command=lambda: move(-1, -1), **btn_style).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(grid, text="↑", command=lambda: move(0, -1), **btn_style).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(grid, text="↗", command=lambda: move(1, -1), **btn_style).grid(row=0, column=2, padx=4, pady=4)

        tk.Button(grid, text="←", command=lambda: move(-1, 0), **btn_style).grid(row=1, column=0, padx=4, pady=4)
        tk.Button(grid, text="•", command=lambda: move(0, 0), **btn_style).grid(row=1, column=1, padx=4, pady=4)
        tk.Button(grid, text="→", command=lambda: move(1, 0), **btn_style).grid(row=1, column=2, padx=4, pady=4)

        tk.Button(grid, text="↙", command=lambda: move(-1, 1), **btn_style).grid(row=2, column=0, padx=4, pady=4)
        tk.Button(grid, text="↓", command=lambda: move(0, 1), **btn_style).grid(row=2, column=1, padx=4, pady=4)
        tk.Button(grid, text="↘", command=lambda: move(1, 1), **btn_style).grid(row=2, column=2, padx=4, pady=4)

        tk.Button(
            win, text="Tutup", bg="#444", fg="white",
            font=("Segoe UI", 9), bd=0, padx=16, pady=4,
            cursor="hand2", command=win.destroy
        ).pack(pady=(4, 10))

    # ── Edit actions ─────────────────────────────────────────────────
    def _undo(self):
        result = self.history.undo(self.state.objects, self.canvas_widget.get_base_image())
        if result is not None:
            self.state.objects = result.get("objects", [])
            if result.get("image") is not None:
                self.canvas_widget.set_base_image(result["image"])
            else:
                self.canvas_widget.redraw()

    def _redo(self):
        result = self.history.redo(self.state.objects, self.canvas_widget.get_base_image())
        if result is not None:
            self.state.objects = result.get("objects", [])
            if result.get("image") is not None:
                self.canvas_widget.set_base_image(result["image"])
            else:
                self.canvas_widget.redraw()

    def _clear(self):
        self.history.save(self.state.objects, self.canvas_widget.get_base_image())
        self.state.clear()
        self.canvas_widget.redraw()

    def _new_canvas(self):
        self.history.clear()
        self.state.clear()
        from PIL import Image
        self.canvas_widget.set_base_image(Image.new(
            "RGB", (self.state.width, self.state.height), "white"
        ))

    def _save(self):
        export_canvas(
            self.canvas_widget._canvas,
            self.state.width, self.state.height,
            self.canvas_widget.get_composited_image()
        )

    def _bind_shortcuts(self):
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())
        self.root.bind("<Control-s>", lambda e: self._save())
        self.root.bind("<Delete>",    lambda e: self._delete_selected())

    def _delete_selected(self):
        idx = self.state.selected_index
        if idx >= 0:
            self.history.save(self.state.objects)
            self.state.remove_object(idx)
            self.state.selected_index = -1
            self.canvas_widget.redraw()
