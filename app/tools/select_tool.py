"""Tool seleksi objek dan crop canvas."""
import tkinter as tk
from app.tools.base_tool import BaseTool


class SelectTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn):
        super().__init__(state, canvas, redraw_fn)
        self._rect_id = None
        self._dragging = False
        self._last_pos = None

    def on_press(self, event):
        super().on_press(event)
        self._clear_preview()
        # Cek apakah ada objek yang di-klik
        self.state.selected_index = self._hit_test(event.x, event.y)
        if self.state.selected_index >= 0:
            self._dragging = True
            self._last_pos = (event.x, event.y)
        self.redraw()

    def on_drag(self, event):
        if self._dragging and self.state.selected_index >= 0:
            dx = event.x - self._last_pos[0]
            dy = event.y - self._last_pos[1]
            obj = self.state.objects[self.state.selected_index]
            obj["points"] = [(x + dx, y + dy) for x, y in obj.get("points", [])]
            self._last_pos = (event.x, event.y)
            self.redraw()
            return
        self._clear_preview()
        self._preview_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="#00b4d8", dash=(4, 4), width=1
        )

    def on_release(self, event):
        self._clear_preview()
        self._dragging = False
        self._last_pos = None

    def _hit_test(self, x, y) -> int:
        """Cari index objek yang mengandung titik (x,y). Return -1 jika tidak ada."""
        for i, obj in enumerate(reversed(self.state.objects)):
            pts = obj.get("points", [])
            if not pts:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            if min(xs)-10 <= x <= max(xs)+10 and min(ys)-10 <= y <= max(ys)+10:
                return len(self.state.objects) - 1 - i
        return -1
