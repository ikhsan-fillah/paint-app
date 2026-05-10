"""Canvas utama dengan resize handles dan event mouse."""
import tkinter as tk
from PIL import Image, ImageTk
from app.config import (
    COLOR_BG_WORKSPACE, COLOR_ACCENT, CANVAS_BG,
    TOOL_PENCIL, TOOL_SELECT, TOOL_FILL,
    TOOL_EYEDROPPER, TOOL_ERASER, TOOL_TRANSFORM
)

HANDLE_SIZE = 8


class CanvasWidget(tk.Frame):
    def __init__(self, parent, state, history, tool_registry, on_cursor_move):
        super().__init__(parent, bg=COLOR_BG_WORKSPACE)
        self.state = state
        self.history = history
        self.tool_registry = tool_registry
        self.on_cursor_move = on_cursor_move

        self._pil_image: Image.Image = Image.new(
            "RGB", (state.width, state.height), CANVAS_BG
        )
        self._tk_image = None

        self._resize_handle = None
        self._drag_start = None

        self._build()
        self._draw_all()

    def _build(self):
        self._canvas = tk.Canvas(
            self, bg=COLOR_BG_WORKSPACE,
            highlightthickness=0, cursor="crosshair"
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._canvas.bind("<ButtonPress-1>",   self._on_press)
        self._canvas.bind("<B1-Motion>",        self._on_drag)
        self._canvas.bind("<ButtonRelease-1>",  self._on_release)
        self._canvas.bind("<Double-Button-1>",  self._on_dbl)
        self._canvas.bind("<Motion>",           self._on_motion)

    # ── PIL image access ──────────────────────────────────────────────
    def get_pil_image(self):
        return self._pil_image.copy()

    def set_pil_image(self, img: Image.Image):
        self._pil_image = img
        self._draw_all()

    def resize_canvas(self, new_w: int, new_h: int):
        """Ubah ukuran canvas via dialog Crop — konten lama dipertahankan."""
        self.history.save(self.state.objects)
        new_img = Image.new("RGB", (new_w, new_h), CANVAS_BG)
        paste_w = min(self._pil_image.width,  new_w)
        paste_h = min(self._pil_image.height, new_h)
        new_img.paste(self._pil_image.crop((0, 0, paste_w, paste_h)), (0, 0))
        self._pil_image   = new_img
        self.state.width  = new_w
        self.state.height = new_h
        self._draw_all()

    # ── Koordinat ─────────────────────────────────────────────────────
    def _canvas_origin(self):
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        sw, sh = self.state.canvas_pixel_size()
        ox = max(0, (cw - sw) // 2)
        oy = max(0, (ch - sh) // 2)
        return ox, oy

    def _screen_to_canvas(self, sx, sy):
        ox, oy = self._canvas_origin()
        scale = self.state.zoom / 100
        return int((sx - ox) / scale), int((sy - oy) / scale)

    # ── Draw ──────────────────────────────────────────────────────────
    def _draw_all(self):
        self._canvas.delete("all")
        sw, sh = self.state.canvas_pixel_size()
        ox, oy = self._canvas_origin()

        render = self._pil_image.resize((sw, sh), Image.NEAREST)
        self._tk_image = ImageTk.PhotoImage(render)
        self._canvas.create_image(ox, oy, anchor=tk.NW, image=self._tk_image)

        for i, obj in enumerate(self.state.objects):
            self._render_object(obj, ox, oy, i == self.state.selected_index)

        self._canvas.create_rectangle(
            ox-1, oy-1, ox+sw, oy+sh,
            outline="#555", width=1
        )
        self._draw_handles(ox, oy, sw, sh)

        if self.state.active_tool == "polygon":
            self._draw_polygon_preview(ox, oy)

    def _draw_handles(self, ox, oy, sw, sh):
        positions = {
            "right":  (ox+sw,    oy+sh//2),
            "bottom": (ox+sw//2, oy+sh),
            "corner": (ox+sw,    oy+sh),
        }
        for name, (hx, hy) in positions.items():
            self._canvas.create_rectangle(
                hx-HANDLE_SIZE//2, hy-HANDLE_SIZE//2,
                hx+HANDLE_SIZE//2, hy+HANDLE_SIZE//2,
                fill="white", outline="#666", tags=("handle", name)
            )

    def _draw_polygon_preview(self, ox, oy):
        tool = self.tool_registry.get("polygon")
        if tool and hasattr(tool, '_polygon_points') and len(tool._polygon_points) >= 2:
            scale = self.state.zoom / 100
            pts = []
            for x, y in tool._polygon_points:
                pts.extend([ox + x*scale, oy + y*scale])
            self._canvas.create_line(pts, fill="#00b4d8", dash=(4, 3))

    def _render_object(self, obj, ox, oy, selected=False):
        scale  = self.state.zoom / 100
        otype  = obj.get("type")
        color  = obj.get("color", "#000000")
        width  = max(1, int(obj.get("width", 1) * scale))
        dash   = obj.get("dash", ())
        fill   = obj.get("bg_color", "") if obj.get("fill") else ""

        def sc(pts):
            return [(ox + x * scale, oy + y * scale) for x, y in pts]

        if otype in ("line", "pencil", "eraser"):
            pts = sc(obj["points"])
            if len(pts) >= 2:
                flat = [c for p in pts for c in p]
                self._canvas.create_line(
                    flat, fill=color, width=width,
                    dash=dash, capstyle=tk.ROUND, joinstyle=tk.ROUND
                )
        elif otype == "rect":
            pts = sc(obj["points"])
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            self._canvas.create_rectangle(
                min(xs), min(ys), max(xs), max(ys),
                outline=color, fill=fill, width=width, dash=dash
            )
        elif otype in ("circle", "ellipse"):
            pts = sc(obj["points"])
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            self._canvas.create_oval(
                min(xs), min(ys), max(xs), max(ys),
                outline=color, fill=fill, width=width, dash=dash
            )
        elif otype in ("triangle", "polygon"):
            pts = sc(obj["points"])
            flat = [c for p in pts for c in p]
            self._canvas.create_polygon(
                flat, outline=color, fill=fill, width=width
            )

        if selected:
            pts = sc(obj["points"])
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            self._canvas.create_rectangle(
                min(xs)-4, min(ys)-4, max(xs)+4, max(ys)+4,
                outline=COLOR_ACCENT, dash=(4, 3), width=1
            )

    # ── Events ────────────────────────────────────────────────────────
    def _hit_handle(self, x, y):
        sw, sh = self.state.canvas_pixel_size()
        ox, oy = self._canvas_origin()
        handles = {
            "corner": (ox+sw, oy+sh),
            "right":  (ox+sw, oy+sh//2),
            "bottom": (ox+sw//2, oy+sh),
        }
        for name, (hx, hy) in handles.items():
            if abs(x-hx) <= HANDLE_SIZE and abs(y-hy) <= HANDLE_SIZE:
                return name
        return None

    def _on_press(self, event):
        h = self._hit_handle(event.x, event.y)
        if h:
            self._resize_handle = h
            self._drag_start = (event.x, event.y,
                                self.state.width, self.state.height)
            return
        cx, cy = self._screen_to_canvas(event.x, event.y)
        if 0 <= cx < self.state.width and 0 <= cy < self.state.height:
            self.history.save(self.state.objects)
            tool = self._active_tool()
            if tool:
                fake = type('E', (), {'x': cx, 'y': cy})()
                tool.on_press(fake)

    def _on_drag(self, event):
        if self._resize_handle and self._drag_start:
            sx, sy, ow, oh = self._drag_start
            dx, dy = event.x - sx, event.y - sy
            scale = self.state.zoom / 100
            if self._resize_handle in ("right", "corner"):
                self.state.width  = max(100, ow + int(dx / scale))
            if self._resize_handle in ("bottom", "corner"):
                self.state.height = max(100, oh + int(dy / scale))
            new_img = Image.new("RGB", (self.state.width, self.state.height), CANVAS_BG)
            paste_w = min(self._pil_image.width,  self.state.width)
            paste_h = min(self._pil_image.height, self.state.height)
            new_img.paste(self._pil_image.crop((0, 0, paste_w, paste_h)), (0, 0))
            self._pil_image = new_img
            self._draw_all()
            return
        cx, cy = self._screen_to_canvas(event.x, event.y)
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy})()
            tool.on_drag(fake)
            self._draw_all()

    def _on_release(self, event):
        if self._resize_handle:
            self._resize_handle = None
            self._drag_start = None
            return
        cx, cy = self._screen_to_canvas(event.x, event.y)
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy})()
            tool.on_release(fake)
        self._draw_all()

    def _on_dbl(self, event):
        cx, cy = self._screen_to_canvas(event.x, event.y)
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy})()
            tool.on_double_click(fake)

    def _on_motion(self, event):
        cx, cy = self._screen_to_canvas(event.x, event.y)
        self.on_cursor_move(cx, cy)
        h = self._hit_handle(event.x, event.y)
        if h == "corner":
            self._canvas.config(cursor="size_nw_se")
        elif h == "right":
            self._canvas.config(cursor="size_we")
        elif h == "bottom":
            self._canvas.config(cursor="size_ns")
        else:
            self._canvas.config(cursor="crosshair")

    def _active_tool(self):
        return self.tool_registry.get(self.state.active_tool)

    def redraw(self):
        self._draw_all()

    def zoom_update(self, pct):
        self.state.zoom = pct
        self._draw_all()
