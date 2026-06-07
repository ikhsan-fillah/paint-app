"""Tool paint bucket — flood fill pada canvas."""
import math
from app.tools.base_tool import BaseTool
from PIL import Image, ImageChops


class FillTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn,
                 get_composited_image_fn, get_base_image_fn, set_base_image_fn):
        super().__init__(state, canvas, redraw_fn)
        self.get_composited_image = get_composited_image_fn
        self.get_base_image = get_base_image_fn
        self.set_base_image = set_base_image_fn

    def on_press(self, event):
        x, y = event.x, event.y
        comp = self.get_composited_image()
        if comp is None or x >= comp.width or y >= comp.height or x < 0 or y < 0:
            return
        fill_rgb = self._hex_to_rgb(self.state.fg_color)

        if self._fill_vector_object(x, y, fill_rgb):
            self.redraw()
            return

        old_rgb = comp.getpixel((x, y))
        if len(old_rgb) == 4:
            old_rgb = old_rgb[:3]
        if old_rgb == fill_rgb:
            return
        before = comp.copy()
        self._flood_fill_pil(comp, x, y, fill_rgb, old_rgb)

        diff = ImageChops.difference(before, comp)
        if diff.getbbox() is None:
            return

        mask = diff.convert("L").point(lambda v: 255 if v else 0)
        base = self.get_base_image()
        fill_layer = Image.new("RGB", base.size, fill_rgb)
        base.paste(fill_layer, mask=mask)
        self.set_base_image(base)
        self.redraw()

    def on_drag(self, event):
        pass

    def on_release(self, event):
        pass

    def _flood_fill_pil(self, img, x, y, fill_color, old_color):
        from collections import deque
        w, h = img.size
        queue = deque([(x, y)])
        visited = set()
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) in visited:
                continue
            if cx < 0 or cy < 0 or cx >= w or cy >= h:
                continue
            px = img.getpixel((cx, cy))
            if len(px) == 4:
                px = px[:3]
            if px != old_color:
                continue
            img.putpixel((cx, cy), fill_color)
            visited.add((cx, cy))
            queue.extend([(cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)])

    def _fill_vector_object(self, x, y, fill_rgb):
        for idx in range(len(self.state.objects) - 1, -1, -1):
            obj = self.state.objects[idx]
            if self._point_in_object(obj, x, y):
                obj["fill"] = True
                obj["bg_color"] = self._rgb_to_hex(fill_rgb)
                return True
        return False

    def _point_in_object(self, obj, x, y):
        otype = obj.get("type")
        if otype == "rect":
            return self._point_in_polygon(x, y, obj.get("points", []))
        if otype in ("triangle", "polygon"):
            return self._point_in_polygon(x, y, obj.get("points", []))
        if otype in ("circle", "ellipse"):
            pts = self._sorted_by_angle(obj.get("points", []))
            if len(pts) >= 3 and self._point_in_polygon(x, y, pts):
                return True
        if otype == "circle":
            cx = obj.get("cx")
            cy = obj.get("cy")
            radius = obj.get("r")
            if cx is None or cy is None or radius is None:
                return False
            return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
        if otype == "ellipse":
            cx = obj.get("cx")
            cy = obj.get("cy")
            rx = obj.get("rx")
            ry = obj.get("ry")
            if cx is None or cy is None or rx in (None, 0) or ry in (None, 0):
                return False
            value = ((x - cx) ** 2) / (rx ** 2) + ((y - cy) ** 2) / (ry ** 2)
            return value <= 1.0
        return False

    @staticmethod
    def _sorted_by_angle(points):
        if len(points) < 3:
            return points
        unique = list({p for p in points})
        cx = sum(p[0] for p in unique) / len(unique)
        cy = sum(p[1] for p in unique) / len(unique)
        return sorted(unique, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

    @staticmethod
    def _point_in_polygon(x, y, points):
        if len(points) < 3:
            return False
        inside = False
        prev_x, prev_y = points[-1]
        for curr_x, curr_y in points:
            crosses = ((curr_y > y) != (prev_y > y))
            if crosses:
                slope_x = (prev_x - curr_x) * (y - curr_y) / ((prev_y - curr_y) or 1e-9) + curr_x
                if x < slope_x:
                    inside = not inside
            prev_x, prev_y = curr_x, curr_y
        return inside

    @staticmethod
    def _rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    @staticmethod
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
