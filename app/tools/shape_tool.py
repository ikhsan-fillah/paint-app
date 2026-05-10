"""Tool shapes: Line, Rect, Circle, Ellipse, Triangle, Polygon."""
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
    def __init__(self, state, canvas, redraw_fn):
        super().__init__(state, canvas, redraw_fn)
        self._polygon_points = []

    # ── Helpers preview ──────────────────────────────────────────────
    def _preview_line(self, x0, y0, x1, y1):
        self._clear_preview()
        self._preview_id = self.canvas.create_line(
            x0, y0, x1, y1,
            fill=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )

    def _preview_rect(self, x0, y0, x1, y1):
        self._clear_preview()
        kw = dict(
            outline=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )
        if self.state.fill_shape:
            kw["fill"] = self.state.bg_color
        self._preview_id = self.canvas.create_rectangle(x0, y0, x1, y1, **kw)

    def _preview_oval(self, x0, y0, x1, y1):
        self._clear_preview()
        kw = dict(
            outline=self.state.fg_color,
            width=self.state.line_width,
            dash=self.state.get_dash_pattern()
        )
        if self.state.fill_shape:
            kw["fill"] = self.state.bg_color
        self._preview_id = self.canvas.create_oval(x0, y0, x1, y1, **kw)

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
            self._preview_id = self.canvas.create_polygon(
                pts, outline=self.state.fg_color,
                fill=self.state.bg_color if self.state.fill_shape else "",
                width=self.state.line_width
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
