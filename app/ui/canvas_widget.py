"""Canvas utama dengan resize handles dan event mouse."""
import math
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
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
        self._stroke_active = False

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
    def get_base_image(self):
        return self._pil_image.copy()

    def set_base_image(self, img: Image.Image):
        self._pil_image = img
        self._draw_all()

    def get_composited_image(self):
        img = self._pil_image.copy()
        return self._draw_objects_to_image(img)

    def flatten_objects_to_base(self):
        if not self.state.objects:
            return
        img = self.get_composited_image()
        self._pil_image = img
        self.state.objects = []
        self.state.selected_index = -1
        if hasattr(self.state, "selected_indices"):
            self.state.selected_indices = []

    def _sorted_by_angle(self, pts):
        if len(pts) < 3:
            return pts
        unique = list({p for p in pts})
        cx = sum(p[0] for p in unique) / len(unique)
        cy = sum(p[1] for p in unique) / len(unique)
        return sorted(unique, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    def _rgba(self, hex_color, opacity_pct):
        h = hex_color.lstrip('#')
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        a = int(max(0, min(100, opacity_pct)) * 255 / 100)
        return (r, g, b, a)

    def _draw_round_path(self, draw, points, width, color):
        if len(points) < 2:
            return
        draw.line(points, fill=color, width=width)
        r = max(1, width // 2)
        for x, y in points:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    def _draw_round_mask(self, draw, points, width):
        if len(points) < 2:
            return
        draw.line(points, fill=255, width=width)
        r = max(1, width // 2)
        for x, y in points:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=255)

    def _apply_object_erasers(self, layer, obj):
        erasers = obj.get("erasers", [])
        if not erasers:
            return layer
        alpha = layer.getchannel("A")
        mask = Image.new("L", layer.size, 0)
        draw = ImageDraw.Draw(mask)
        for eraser in erasers:
            points = eraser.get("points", [])
            width = max(1, int(eraser.get("width", 1)))
            self._draw_round_mask(draw, points, width)
        alpha.paste(0, mask=mask)
        layer.putalpha(alpha)
        return layer

    def _draw_objects_to_image(self, img: Image.Image):
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        for obj in self.state.objects:
            otype = obj.get("type")
            color = obj.get("color", "#000000")
            width = max(1, int(obj.get("width", 1)))
            opacity = obj.get("opacity", 100)
            stroke_rgba = self._rgba(color, opacity)
            fill_rgba = self._rgba(obj.get("bg_color", "#000000"), opacity) if obj.get("fill") else None

            layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)

            if otype == "eraser":
                continue
            if otype in ("line", "pencil"):
                pts = obj.get("points", [])
                if len(pts) >= 2:
                    self._draw_round_path(draw, pts, width, stroke_rgba)
            elif otype in ("rect", "triangle", "polygon"):
                pts = obj.get("points", [])
                if len(pts) >= 3:
                    if fill_rgba is not None:
                        draw.polygon(pts, fill=fill_rgba)
                    self._draw_round_path(draw, pts + [pts[0]], width, stroke_rgba)
                elif len(pts) == 2:
                    self._draw_round_path(draw, pts, width, stroke_rgba)
            elif otype in ("circle", "ellipse"):
                pts = self._sorted_by_angle(obj.get("points", []))
                if len(pts) >= 3:
                    if fill_rgba is not None:
                        draw.polygon(pts, fill=fill_rgba)
                    self._draw_round_path(draw, pts + [pts[0]], width, stroke_rgba)

            layer = self._apply_object_erasers(layer, obj)
            img = Image.alpha_composite(img, layer)

        return img.convert("RGB")

    def resize_canvas(self, new_w: int, new_h: int):
        """Ubah ukuran canvas via dialog Crop — konten lama dipertahankan."""
        self.history.save(self.state.objects, self._pil_image)
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

    def _canvas_to_screen(self, x, y):
        ox, oy = self._canvas_origin()
        scale = self.state.zoom / 100
        return ox + x * scale, oy + y * scale

    def points_to_screen(self, points):
        return [self._canvas_to_screen(x, y) for x, y in points]

    def _in_bounds(self, x, y):
        return 0 <= x < self.state.width and 0 <= y < self.state.height

    def _clip_line(self, x0, y0, x1, y1):
        """Clip a line segment to the canvas bounds. Return None or ((x0,y0),(x1,y1))."""
        xmin, ymin = 0.0, 0.0
        xmax, ymax = float(self.state.width - 1), float(self.state.height - 1)
        dx = x1 - x0
        dy = y1 - y0

        p = [-dx, dx, -dy, dy]
        q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]

        u1, u2 = 0.0, 1.0
        for pi, qi in zip(p, q):
            if pi == 0:
                if qi < 0:
                    return None
            else:
                t = qi / pi
                if pi < 0:
                    if t > u2:
                        return None
                    if t > u1:
                        u1 = t
                else:
                    if t < u1:
                        return None
                    if t < u2:
                        u2 = t

        nx0 = x0 + u1 * dx
        ny0 = y0 + u1 * dy
        nx1 = x0 + u2 * dx
        ny1 = y0 + u2 * dy
        return (nx0, ny0), (nx1, ny1)

    def _clip_polyline(self, points):
        segments = []
        for i in range(len(points) - 1):
            (x0, y0) = points[i]
            (x1, y1) = points[i + 1]
            clipped = self._clip_line(x0, y0, x1, y1)
            if clipped:
                segments.append(clipped)
        return segments

    def _clip_polygon(self, points):
        """Sutherland-Hodgman polygon clipping to canvas bounds."""
        if not points:
            return []

        def clip_edge(pts, edge_fn):
            if not pts:
                return []
            output = []
            prev = pts[-1]
            prev_inside = edge_fn(prev)
            for curr in pts:
                curr_inside = edge_fn(curr)
                if curr_inside:
                    if not prev_inside:
                        output.append(intersection(prev, curr))
                    output.append(curr)
                elif prev_inside:
                    output.append(intersection(prev, curr))
                prev, prev_inside = curr, curr_inside
            return output

        xmin, ymin = 0.0, 0.0
        xmax, ymax = float(self.state.width - 1), float(self.state.height - 1)

        def intersection(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            dx = x2 - x1
            dy = y2 - y1
            t = 0.0

            if edge == "left":
                t = (xmin - x1) / dx if dx != 0 else 0.0
            elif edge == "right":
                t = (xmax - x1) / dx if dx != 0 else 0.0
            elif edge == "bottom":
                t = (ymax - y1) / dy if dy != 0 else 0.0
            elif edge == "top":
                t = (ymin - y1) / dy if dy != 0 else 0.0
            return (x1 + t * dx, y1 + t * dy)

        pts = points
        for edge, fn in [
            ("left", lambda p: p[0] >= xmin),
            ("right", lambda p: p[0] <= xmax),
            ("top", lambda p: p[1] >= ymin),
            ("bottom", lambda p: p[1] <= ymax),
        ]:
            pts = clip_edge(pts, fn)
        return pts

    # ── Draw ──────────────────────────────────────────────────────────
    def _draw_all(self):
        self._canvas.delete("all")
        sw, sh = self.state.canvas_pixel_size()
        ox, oy = self._canvas_origin()

        render = self.get_composited_image().resize((sw, sh), Image.NEAREST)
        self._tk_image = ImageTk.PhotoImage(render)
        self._canvas.create_image(ox, oy, anchor=tk.NW, image=self._tk_image)

        selected_indices = getattr(self.state, "selected_indices", [])
        if not selected_indices and 0 <= self.state.selected_index < len(self.state.objects):
            selected_indices = [self.state.selected_index]

        for idx in selected_indices:
            if 0 <= idx < len(self.state.objects):
                self._render_object(self.state.objects[idx], ox, oy, True)

        self._canvas.create_rectangle(
            ox-1, oy-1, ox+sw, oy+sh,
            outline="#555", width=1
        )
        self._draw_handles(ox, oy, sw, sh)

        if self.state.active_tool == "polygon":
            self._draw_polygon_preview(ox, oy)

    def _draw_handles(self, ox, oy, sw, sh):
        positions = {
            "top_left":     (ox,       oy),
            "top":          (ox+sw//2, oy),
            "top_right":    (ox+sw,    oy),
            "left":         (ox,       oy+sh//2),
            "right":        (ox+sw,    oy+sh//2),
            "bottom_left":  (ox,       oy+sh),
            "bottom":       (ox+sw//2, oy+sh),
            "bottom_right": (ox+sw,    oy+sh),
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
            segments = self._clip_polyline(tool._polygon_points)
            for (p0, p1) in segments:
                self._canvas.create_line(
                    ox + p0[0] * scale, oy + p0[1] * scale,
                    ox + p1[0] * scale, oy + p1[1] * scale,
                    fill="#00b4d8", dash=(4, 3)
                )

    def _render_object(self, obj, ox, oy, selected=False):
        scale  = self.state.zoom / 100
        otype  = obj.get("type")
        color  = obj.get("color", "#000000")
        width  = max(1, int(obj.get("width", 1) * scale))
        dash   = obj.get("dash", ())
        fill   = obj.get("bg_color", "") if obj.get("fill") else ""

        def sc(pts):
            return [(ox + x * scale, oy + y * scale) for x, y in pts]

        def draw_outline(points):
            if len(points) < 2:
                return
            closed = points + [points[0]]
            segments = self._clip_polyline(closed)
            for (p0, p1) in segments:
                seg = sc([p0, p1])
                self._canvas.create_line(
                    seg[0][0], seg[0][1], seg[1][0], seg[1][1],
                    fill=color, width=width, dash=dash,
                    capstyle=tk.ROUND, joinstyle=tk.ROUND
                )

        if otype in ("line", "pencil", "eraser"):
            pts = obj.get("points", [])
            if len(pts) >= 2:
                segments = self._clip_polyline(pts)
                for (p0, p1) in segments:
                    seg = sc([p0, p1])
                    self._canvas.create_line(
                        seg[0][0], seg[0][1], seg[1][0], seg[1][1],
                        fill=color, width=width,
                        dash=dash, capstyle=tk.ROUND, joinstyle=tk.ROUND
                    )
        elif otype == "rect":
            pts = obj.get("points", [])
            if fill:
                clipped = self._clip_polygon(pts)
                if len(clipped) >= 3:
                    flat = [c for p in sc(clipped) for c in p]
                    self._canvas.create_polygon(
                        flat, outline=color, fill=fill, width=width, dash=dash
                    )
            else:
                draw_outline(pts)
        elif otype in ("circle", "ellipse"):
            pts = self._sorted_by_angle(obj.get("points", []))
            if fill:
                clipped = self._clip_polygon(pts)
                if len(clipped) >= 3:
                    flat = [c for p in sc(clipped) for c in p]
                    self._canvas.create_polygon(
                        flat, outline=color, fill=fill, width=width, dash=dash
                    )
            else:
                draw_outline(pts)
        elif otype in ("triangle", "polygon"):
            pts = obj.get("points", [])
            if fill:
                clipped = self._clip_polygon(pts)
                if len(clipped) >= 3:
                    flat = [c for p in sc(clipped) for c in p]
                    self._canvas.create_polygon(
                        flat, outline=color, fill=fill, width=width, dash=dash
                    )
            else:
                draw_outline(pts)

        if selected:
            for eraser in obj.get("erasers", []):
                points = eraser.get("points", [])
                if len(points) < 2:
                    continue
                width = max(1, int(eraser.get("width", 1) * scale))
                for (p0, p1) in self._clip_polyline(points):
                    seg = sc([p0, p1])
                    self._canvas.create_line(
                        seg[0][0], seg[0][1], seg[1][0], seg[1][1],
                        fill=CANVAS_BG, width=width,
                        capstyle=tk.ROUND, joinstyle=tk.ROUND
                    )
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
            "top_left":     (ox,       oy),
            "top":          (ox+sw//2, oy),
            "top_right":    (ox+sw,    oy),
            "left":         (ox,       oy+sh//2),
            "right":        (ox+sw,    oy+sh//2),
            "bottom_left":  (ox,       oy+sh),
            "bottom":       (ox+sw//2, oy+sh),
            "bottom_right": (ox+sw,    oy+sh),
        }
        for name, (hx, hy) in handles.items():
            if abs(x-hx) <= HANDLE_SIZE and abs(y-hy) <= HANDLE_SIZE:
                return name
        return None

    def _on_press(self, event):
        h = self._hit_handle(event.x, event.y)
        if h:
            self.history.save(self.state.objects, self._pil_image)
            self._resize_handle = h
            self._drag_start = (
                event.x, event.y,
                self.state.width, self.state.height,
                self._pil_image.copy()
            )
            return
        cx, cy = self._screen_to_canvas(event.x, event.y)
        if not self._in_bounds(cx, cy):
            self._stroke_active = False
            return
        self._stroke_active = True
        self.history.save(self.state.objects, self._pil_image)
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy, 'sx': event.x, 'sy': event.y})()
            tool.on_press(fake)

    def _on_drag(self, event):
        if self._resize_handle and self._drag_start:
            sx, sy, ow, oh, base_img = self._drag_start
            dx, dy = event.x - sx, event.y - sy
            scale = self.state.zoom / 100
            dwx = int(dx / scale)
            dhy = int(dy / scale)

            new_w = ow
            new_h = oh

            if self._resize_handle in ("right", "top_right", "bottom_right"):
                new_w = max(100, ow + dwx)
            if self._resize_handle in ("left", "top_left", "bottom_left"):
                new_w = max(100, ow - dwx)

            if self._resize_handle in ("bottom", "bottom_left", "bottom_right"):
                new_h = max(100, oh + dhy)
            if self._resize_handle in ("top", "top_left", "top_right"):
                new_h = max(100, oh - dhy)

            self.state.width = new_w
            self.state.height = new_h

            new_img = Image.new("RGB", (new_w, new_h), CANVAS_BG)

            if self._resize_handle in ("left", "top_left", "bottom_left"):
                if new_w >= ow:
                    offset_x = new_w - ow
                    crop_x = 0
                    crop_w = ow
                else:
                    offset_x = 0
                    crop_x = ow - new_w
                    crop_w = new_w
            else:
                offset_x = 0
                crop_x = 0
                crop_w = min(new_w, ow)

            if self._resize_handle in ("top", "top_left", "top_right"):
                if new_h >= oh:
                    offset_y = new_h - oh
                    crop_y = 0
                    crop_h = oh
                else:
                    offset_y = 0
                    crop_y = oh - new_h
                    crop_h = new_h
            else:
                offset_y = 0
                crop_y = 0
                crop_h = min(new_h, oh)

            crop = base_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
            new_img.paste(crop, (offset_x, offset_y))
            self._pil_image = new_img
            self._draw_all()
            return
        if not self._stroke_active:
            return
        cx, cy = self._screen_to_canvas(event.x, event.y)
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy, 'sx': event.x, 'sy': event.y})()
            tool.on_drag(fake)

    def _on_release(self, event):
        if self._resize_handle:
            self._resize_handle = None
            self._drag_start = None
            return
        if not self._stroke_active:
            return
        cx, cy = self._screen_to_canvas(event.x, event.y)
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy, 'sx': event.x, 'sy': event.y})()
            tool.on_release(fake)
        self._draw_all()
        self._stroke_active = False

    def _on_dbl(self, event):
        cx, cy = self._screen_to_canvas(event.x, event.y)
        if not self._in_bounds(cx, cy):
            return
        tool = self._active_tool()
        if tool:
            fake = type('E', (), {'x': cx, 'y': cy})()
            tool.on_double_click(fake)

    def _on_motion(self, event):
        cx, cy = self._screen_to_canvas(event.x, event.y)
        self.on_cursor_move(cx, cy)
        h = self._hit_handle(event.x, event.y)
        if h in ("top_left", "bottom_right"):
            self._canvas.config(cursor="size_nw_se")
        elif h in ("top_right", "bottom_left"):
            self._canvas.config(cursor="size_ne_sw")
        elif h in ("right", "left"):
            self._canvas.config(cursor="size_we")
        elif h in ("top", "bottom"):
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
