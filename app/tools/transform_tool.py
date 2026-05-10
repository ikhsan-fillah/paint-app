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

    def _get_selected(self):
        idx = self.state.selected_index
        if 0 <= idx < len(self.state.objects):
            return self.state.objects[idx]
        return None

    def _center_of(self, obj):
        pts = obj.get("points", [])
        if not pts:
            return 0, 0
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        return (min(xs)+max(xs))//2, (min(ys)+max(ys))//2

    def apply_translate(self, tx, ty):
        obj = self._get_selected()
        if obj:
            obj["points"] = T.translate(obj["points"], tx, ty)
            self.redraw()

    def apply_rotate(self, angle_deg):
        obj = self._get_selected()
        if obj:
            cx, cy = self._center_of(obj)
            obj["points"] = T.rotate(obj["points"], angle_deg, cx, cy)
            self.redraw()

    def apply_scale(self, sx, sy):
        obj = self._get_selected()
        if obj:
            cx, cy = self._center_of(obj)
            obj["points"] = T.scale(obj["points"], sx, sy, cx, cy)
            self.redraw()

    def apply_reflect(self, mode):
        obj = self._get_selected()
        if obj:
            fns = {
                "x": T.reflect_x, "y": T.reflect_y,
                "origin": T.reflect_origin, "diagonal": T.reflect_diagonal
            }
            fn = fns.get(mode)
            if fn:
                obj["points"] = fn(obj["points"])
                self.redraw()

    def apply_shear(self, shx=0, shy=0):
        obj = self._get_selected()
        if obj:
            if shx != 0:
                obj["points"] = T.shear_x(obj["points"], shx)
            if shy != 0:
                obj["points"] = T.shear_y(obj["points"], shy)
            self.redraw()
