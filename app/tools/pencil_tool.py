"""Tool pensil — freehand drawing."""
from PIL import Image, ImageDraw
from app.tools.base_tool import BaseTool
from app.config import TOOL_ERASER, CANVAS_BG


class PencilTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn,
                 get_base_image_fn=None, set_base_image_fn=None, flatten_fn=None,
                 to_screen_fn=None):
        super().__init__(state, canvas, redraw_fn)
        self._current_points = []
        self._get_base_image = get_base_image_fn
        self._set_base_image = set_base_image_fn
        self._flatten = flatten_fn
        self._to_screen = to_screen_fn

    def on_press(self, event):
        super().on_press(event)
        self._current_points = [(event.x, event.y)]
        if self.state.active_tool == TOOL_ERASER and self._flatten:
            self._flatten()

    def on_drag(self, event):
        x, y = event.x, event.y
        if self.state.active_tool == TOOL_ERASER and self._get_base_image:
            if self._current_points:
                lx, ly = self._current_points[-1]
                img = self._get_base_image()
                img = self._erase_segment(img, (lx, ly), (x, y), self.state.line_width)
                if self._set_base_image:
                    self._set_base_image(img)
        else:
            if self._current_points:
                lx, ly = self._current_points[-1]
                if hasattr(event, 'sx') and hasattr(event, 'sy'):
                    if self._to_screen:
                        sx0, sy0 = self._to_screen(lx, ly)
                    else:
                        sx0, sy0 = lx, ly
                    sx1, sy1 = event.sx, event.sy
                else:
                    if self._to_screen:
                        sx0, sy0 = self._to_screen(lx, ly)
                        sx1, sy1 = self._to_screen(x, y)
                    else:
                        sx0, sy0, sx1, sy1 = lx, ly, x, y
                # Gambar segmen langsung ke canvas untuk performa real-time
                self.canvas.create_line(
                    sx0, sy0, sx1, sy1,
                    fill=self.state.fg_color,
                    width=self.state.line_width,
                    capstyle="round",
                    joinstyle="round"
                )
        self._current_points.append((x, y))

    def on_release(self, event):
        if len(self._current_points) >= 2:
            if self.state.active_tool == TOOL_ERASER:
                pass
            else:
                self.state.add_object({
                    "type": "pencil",
                    "points": list(self._current_points),
                    "color": self.state.fg_color,
                    "width": self.state.line_width,
                    "opacity": self.state.opacity,
                    "dash": (),
                })
        self._current_points = []
        self.redraw()

    @staticmethod
    def _erase_segment(img: Image.Image, p0, p1, width):
        mask = Image.new("L", img.size, 0)
        mdraw = ImageDraw.Draw(mask)
        w = max(1, int(width))
        mdraw.line([p0, p1], fill=255, width=w)
        r = max(1, w // 2)
        for x, y in (p0, p1):
            mdraw.ellipse((x - r, y - r, x + r, y + r), fill=255)
        bg = Image.new("RGB", img.size, CANVAS_BG)
        img.paste(bg, mask=mask)
        return img
