"""Tool seleksi objek dan crop canvas."""
from app.algorithms import transform as T
from app.tools.base_tool import BaseTool


class SelectTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn):
        super().__init__(state, canvas, redraw_fn)
        self._rect_id = None
        self._dragging = False
        self._last_pos = None
        self._selecting_box = False
        self._start_screen = None

    def on_press(self, event):
        super().on_press(event)
        self._clear_preview()
        self._start_screen = (getattr(event, "sx", event.x), getattr(event, "sy", event.y))
        hit_index = self._hit_test(event.x, event.y)
        selected = self._selected_indices()

        if hit_index >= 0:
            if hit_index not in selected:
                selected = [hit_index]
                self._set_selected_indices(selected)
            self._dragging = True
            self._last_pos = (event.x, event.y)
            self._selecting_box = False
        else:
            self._set_selected_indices([])
            self._dragging = False
            self._selecting_box = True
        self.redraw()

    def on_drag(self, event):
        selected = self._selected_indices()
        if self._dragging and selected:
            dx = event.x - self._last_pos[0]
            dy = event.y - self._last_pos[1]
            for idx in selected:
                obj = self.state.objects[idx]
                self._move_object(obj, dx, dy)
            self._last_pos = (event.x, event.y)
            self.redraw()
            return

        if not self._selecting_box:
            return

        self._clear_preview()
        sx0, sy0 = self._start_screen or (getattr(event, "sx", event.x), getattr(event, "sy", event.y))
        self._preview_id = self.canvas.create_rectangle(
            sx0,
            sy0,
            getattr(event, "sx", event.x),
            getattr(event, "sy", event.y),
            outline="#00b4d8", dash=(4, 4), width=1
        )

    def on_release(self, event):
        if self._selecting_box:
            indices = self._hit_test_box(self.start_x, self.start_y, event.x, event.y)
            self._set_selected_indices(indices)
        self._clear_preview()
        self._dragging = False
        self._last_pos = None
        self._selecting_box = False
        self._start_screen = None
        self.redraw()

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

    def _hit_test_box(self, x0, y0, x1, y1):
        left, right = sorted((x0, x1))
        top, bottom = sorted((y0, y1))
        indices = []
        for idx, obj in enumerate(self.state.objects):
            bbox = self._bbox(obj)
            if not bbox:
                continue
            obj_left, obj_top, obj_right, obj_bottom = bbox
            intersects = (
                obj_right >= left and obj_left <= right and
                obj_bottom >= top and obj_top <= bottom
            )
            if intersects:
                indices.append(idx)
        return indices

    def _bbox(self, obj):
        pts = obj.get("points", [])
        if not pts:
            return None
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def _move_object(self, obj, dx, dy):
        obj["points"] = [(x + dx, y + dy) for x, y in obj.get("points", [])]
        mask = obj.get("erase_mask")
        if mask is not None:
            obj["erase_mask"] = T.translate_mask(mask, (self.state.width, self.state.height), dx, dy)
        for eraser in obj.get("erasers", []):
            eraser["points"] = [
                (x + dx, y + dy) for x, y in eraser.get("points", [])
            ]
        if "cx" in obj:
            obj["cx"] += dx
        if "cy" in obj:
            obj["cy"] += dy

    def _selected_indices(self):
        indices = getattr(self.state, "selected_indices", [])
        if indices:
            return [i for i in indices if 0 <= i < len(self.state.objects)]
        if 0 <= self.state.selected_index < len(self.state.objects):
            return [self.state.selected_index]
        return []

    def _set_selected_indices(self, indices):
        self.state.selected_indices = indices
        self.state.selected_index = indices[0] if indices else -1
