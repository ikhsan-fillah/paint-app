"""Tool pensil — freehand drawing."""
from app.tools.base_tool import BaseTool


class PencilTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn):
        super().__init__(state, canvas, redraw_fn)
        self._current_points = []

    def on_press(self, event):
        super().on_press(event)
        self._current_points = [(event.x, event.y)]

    def on_drag(self, event):
        x, y = event.x, event.y
        if self._current_points:
            lx, ly = self._current_points[-1]
            # Gambar segmen langsung ke canvas untuk performa real-time
            self.canvas.create_line(
                lx, ly, x, y,
                fill=self.state.fg_color,
                width=self.state.line_width,
                capstyle="round",
                joinstyle="round"
            )
        self._current_points.append((x, y))

    def on_release(self, event):
        if len(self._current_points) >= 2:
            from app.core.history import History
            self.state.add_object({
                "type": "pencil",
                "points": list(self._current_points),
                "color": self.state.fg_color,
                "width": self.state.line_width,
                "dash": (),
            })
        self._current_points = []
        self.redraw()
