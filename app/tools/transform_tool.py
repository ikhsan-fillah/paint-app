"""Tool transformasi — apply transform ke objek yang dipilih."""
from app.tools.base_tool import BaseTool
from app.algorithms import transform as T


class TransformTool(BaseTool):
    def on_press(self, event):
        pass

    def on_drag(self, event):
        pass

    def on_release(self, event):
        pass

    def _get_selected_indices(self):
        indices = getattr(self.state, "selected_indices", [])
        if indices:
            return [i for i in indices if 0 <= i < len(self.state.objects)]
        if 0 <= self.state.selected_index < len(self.state.objects):
            return [self.state.selected_index]
        return []

    def _center_of(self, obj):
        pts = obj.get("points", [])
        if not pts:
            return 0, 0
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs)+max(xs))//2, (min(ys)+max(ys))//2

    def apply_translate(self, tx, ty):
        indices = self._get_selected_indices()
        if indices:
            for idx in indices:
                obj = self.state.objects[idx]
                obj["points"] = T.translate(obj["points"], tx, ty)
                self._move_object_metadata(obj, tx, ty)
            self.redraw()

    def _move_object_metadata(self, obj, dx, dy):
        self._transform_mask(obj, lambda mask: T.translate_mask(mask, (self.state.width, self.state.height), dx, dy))
        self._transform_erasers(obj, lambda points: T.translate(points, dx, dy))
        if "cx" in obj:
            obj["cx"] += dx
        if "cy" in obj:
            obj["cy"] += dy

    def _transform_erasers(self, obj, transform_fn):
        for eraser in obj.get("erasers", []):
            eraser["points"] = transform_fn(eraser.get("points", []))

    def _transform_mask(self, obj, transform_fn):
        mask = obj.get("erase_mask")
        if mask is not None:
            obj["erase_mask"] = transform_fn(mask)

    def _apply_to_selected(self, transform_fn):
        indices = self._get_selected_indices()
        if indices:
            for idx in indices:
                obj = self.state.objects[idx]
                transform_fn(obj)
            self.redraw()

    def apply_rotate(self, angle_deg):
        def rotate_obj(obj):
            cx, cy = self._center_of(obj)
            obj["points"] = T.rotate(obj["points"], angle_deg, cx, cy)
            self._transform_mask(obj, lambda mask: T.rotate_mask(mask, (self.state.width, self.state.height), angle_deg, cx, cy))
            self._transform_erasers(obj, lambda points: T.rotate(points, angle_deg, cx, cy))

        self._apply_to_selected(rotate_obj)

    def apply_scale(self, sx, sy):
        def scale_obj(obj):
            cx, cy = self._center_of(obj)
            obj["points"] = T.scale(obj["points"], sx, sy, cx, cy)
            self._transform_mask(obj, lambda mask: T.scale_mask(mask, (self.state.width, self.state.height), sx, sy, cx, cy))
            self._transform_erasers(obj, lambda points: T.scale(points, sx, sy, cx, cy))

        self._apply_to_selected(scale_obj)

    def apply_reflect(self, mode):
        def reflect_obj(obj):
            cx, cy = self._center_of(obj)
            if mode == "x":
                obj["points"] = T.reflect_y(obj["points"], cx)
                self._transform_mask(obj, lambda mask: T.reflect_y_mask(mask, (self.state.width, self.state.height), cx))
                self._transform_erasers(obj, lambda points: T.reflect_y(points, cx))
            elif mode == "y":
                obj["points"] = T.reflect_x(obj["points"], cy)
                self._transform_mask(obj, lambda mask: T.reflect_x_mask(mask, (self.state.width, self.state.height), cy))
                self._transform_erasers(obj, lambda points: T.reflect_x(points, cy))
            elif mode == "origin":
                obj["points"] = T.reflect_origin(obj["points"], cx, cy)
                self._transform_mask(obj, lambda mask: T.reflect_origin_mask(mask, (self.state.width, self.state.height), cx, cy))
                self._transform_erasers(obj, lambda points: T.reflect_origin(points, cx, cy))
            elif mode == "diagonal":
                obj["points"] = T.reflect_diagonal(obj["points"], cx, cy)
                self._transform_mask(obj, lambda mask: T.reflect_diagonal_mask(mask, (self.state.width, self.state.height), cx, cy))
                self._transform_erasers(obj, lambda points: T.reflect_diagonal(points, cx, cy))

        self._apply_to_selected(reflect_obj)

    def apply_shear(self, shx=0, shy=0):
        def shear_obj(obj):
            if shx != 0:
                obj["points"] = T.shear_x(obj["points"], shx)
                self._transform_mask(obj, lambda mask: T.shear_x_mask(mask, (self.state.width, self.state.height), shx))
                self._transform_erasers(obj, lambda points: T.shear_x(points, shx))
            if shy != 0:
                obj["points"] = T.shear_y(obj["points"], shy)
                self._transform_mask(obj, lambda mask: T.shear_y_mask(mask, (self.state.width, self.state.height), shy))
                self._transform_erasers(obj, lambda points: T.shear_y(points, shy))

        self._apply_to_selected(shear_obj)
