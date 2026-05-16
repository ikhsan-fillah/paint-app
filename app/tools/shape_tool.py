"""Tool shapes: Line, Rect, Circle, Ellipse, Triangle, Polygon."""
import math
import tkinter as tk
from app.tools.base_tool import BaseTool
from app.algorithms.line import bresenham_line
from app.algorithms.circle import midpoint_circle
from app.algorithms.ellipse import midpoint_ellipse
from app.config import (
    TOOL_LINE, TOOL_RECT, TOOL_CIRCLE,
    TOOL_ELLIPSE, TOOL_TRIANGLE, TOOL_POLYGON
)


class ShapeTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn, to_screen_fn=None):
        super().__init__(state, canvas, redraw_fn)
        self._polygon_points = []
        self._to_screen = to_screen_fn

    # ── Helpers preview ──────────────────────────────────────────────
    def _to_screen_points(self, points):
        if not self._to_screen:
            return points
        return [self._to_screen(x, y) for x, y in points]
    def _clip_line(self, x0, y0, x1, y1):
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

    def _clip_polygon(self, points):
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

    def _ellipse_points(self, x0, y0, x1, y1, steps=72):
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = abs(x1 - x0) / 2.0
        ry = abs(y1 - y0) / 2.0
        if rx == 0 or ry == 0:
            return [(x0, y0), (x1, y1)]
        pts = []
        for i in range(steps):
            a = 2 * math.pi * i / steps
            pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
        return pts

    def _preview_line(self, x0, y0, x1, y1):
        self._clear_preview()
        clipped = self._clip_line(x0, y0, x1, y1)
        if not clipped:
            return
        (cx0, cy0), (cx1, cy1) = clipped
        (sx0, sy0), (sx1, sy1) = self._to_screen_points([(cx0, cy0), (cx1, cy1)])
        self._preview_id = self.canvas.create_line(
            sx0, sy0, sx1, sy1,
            fill=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )

    def _preview_rect(self, x0, y0, x1, y1):
        self._clear_preview()
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        clipped = self._clip_polygon(pts)
        if len(clipped) < 2:
            return
        kw = dict(
            outline=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )
        line_kw = dict(
            fill=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )
        kw["fill"] = self.state.bg_color if self.state.fill_shape else ""
        if len(clipped) >= 3:
            flat = [c for p in self._to_screen_points(clipped) for c in p]
            self._preview_id = self.canvas.create_polygon(flat, **kw)
        else:
            (p0, p1) = clipped
            (sp0, sp1) = self._to_screen_points([p0, p1])
            self._preview_id = self.canvas.create_line(sp0[0], sp0[1], sp1[0], sp1[1], **line_kw)

    def _preview_oval(self, x0, y0, x1, y1):
        self._clear_preview()
        pts = self._ellipse_points(x0, y0, x1, y1)
        clipped = self._clip_polygon(pts)
        if len(clipped) < 2:
            return
        kw = dict(
            outline=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )
        line_kw = dict(
            fill=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )
        kw["fill"] = self.state.bg_color if self.state.fill_shape else ""
        if len(clipped) >= 3:
            flat = [c for p in self._to_screen_points(clipped) for c in p]
            self._preview_id = self.canvas.create_polygon(flat, **kw)
        else:
            (p0, p1) = clipped
            (sp0, sp1) = self._to_screen_points([p0, p1])
            self._preview_id = self.canvas.create_line(sp0[0], sp0[1], sp1[0], sp1[1], **line_kw)

    # ── Event handlers ───────────────────────────────────────────────
    def on_press(self, event):
        tool = self.state.active_tool
        if tool == TOOL_POLYGON:
            if not self._polygon_points:
                self._polygon_points = [(event.x, event.y)]
            else:
                self._polygon_points.append((event.x, event.y))
            self.redraw()
            return
        super().on_press(event)

    def on_drag(self, event):
        tool = self.state.active_tool
        x0, y0 = self.start_x, self.start_y
        x1, y1 = event.x, event.y
        if tool == TOOL_LINE:
            self._preview_line(x0, y0, x1, y1)
        elif tool == TOOL_RECT:
            self._preview_rect(x0, y0, x1, y1)
        elif tool == TOOL_CIRCLE:
            r = int(((x1-x0)**2 + (y1-y0)**2) ** 0.5)
            self._preview_oval(x0-r, y0-r, x0+r, y0+r)
        elif tool == TOOL_ELLIPSE:
            self._preview_oval(x0, y0, x1, y1)
        elif tool == TOOL_TRIANGLE:
            self._clear_preview()
            mid_x = (x0 + x1) // 2
            pts = [mid_x, y0, x1, y1, x0, y1]
            clip_src = [(pts[0], pts[1]), (pts[2], pts[3]), (pts[4], pts[5])]
            clipped = self._clip_polygon(clip_src)
            if len(clipped) >= 3:
                flat = [c for p in self._to_screen_points(clipped) for c in p]
                self._preview_id = self.canvas.create_polygon(
                    flat, outline=self.state.fg_color,
                    fill=self.state.bg_color if self.state.fill_shape else "",
                    width=self.state.line_width,
                    dash=self.state.get_dash_pattern()
                )

    def on_release(self, event):
        tool = self.state.active_tool
        if tool == TOOL_POLYGON:
            return  # polygon selesai saat double-click
        x0, y0 = self.start_x, self.start_y
        x1, y1 = event.x, event.y
        self._clear_preview()
        obj = self._build_object(tool, x0, y0, x1, y1)
        if obj:
            self.state.add_object(obj)
        self.redraw()

    def on_double_click(self, event):
        """Selesaikan polygon."""
        if self.state.active_tool == TOOL_POLYGON and len(self._polygon_points) >= 3:
            self.state.add_object({
                "type": "polygon",
                "points": list(self._polygon_points),
                "color": self.state.fg_color,
                "bg_color": self.state.bg_color,
                "width": self.state.line_width,
                "opacity": self.state.opacity,
                "dash": self.state.get_dash_pattern(),
                "fill": self.state.fill_shape,
            })
            self._polygon_points = []
            self.redraw()

    def _build_object(self, tool, x0, y0, x1, y1):
        common = {
            "color": self.state.fg_color,
            "bg_color": self.state.bg_color,
            "width": self.state.line_width,
            "opacity": self.state.opacity,
            "dash": self.state.get_dash_pattern(),
            "fill": self.state.fill_shape,
        }
        if tool == TOOL_LINE:
            pts = bresenham_line(x0, y0, x1, y1)
            return {"type": "line", "points": pts, **common}
        elif tool == TOOL_RECT:
            pts = [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
            return {"type": "rect", "points": pts, **common}
        elif tool == TOOL_CIRCLE:
            r = int(((x1-x0)**2 + (y1-y0)**2) ** 0.5)
            pts = midpoint_circle(x0, y0, r)
            return {"type": "circle", "points": pts, "cx": x0, "cy": y0, "r": r, **common}
        elif tool == TOOL_ELLIPSE:
            cx, cy = (x0+x1)//2, (y0+y1)//2
            rx, ry = abs(x1-x0)//2, abs(y1-y0)//2
            if rx < 1 or ry < 1:
                return None
            pts = midpoint_ellipse(cx, cy, rx, ry)
            return {"type": "ellipse", "points": pts, "cx":cx,"cy":cy,"rx":rx,"ry":ry, **common}
        elif tool == TOOL_TRIANGLE:
            mid_x = (x0 + x1) // 2
            pts = [(mid_x, y0), (x1, y1), (x0, y1)]
            return {"type": "triangle", "points": pts, **common}
        return None
