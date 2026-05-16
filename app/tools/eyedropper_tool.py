"""Tool eyedropper — ambil warna dari canvas."""
from app.tools.base_tool import BaseTool


class EyedropperTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn, get_composited_image_fn, on_color_picked_fn):
        super().__init__(state, canvas, redraw_fn)
        self.get_composited_image = get_composited_image_fn
        self.on_color_picked = on_color_picked_fn

    def on_press(self, event):
        img = self.get_composited_image()
        if img is None:
            return
        x, y = event.x, event.y
        if x < 0 or y < 0 or x >= img.width or y >= img.height:
            return
        pixel = img.getpixel((x, y))
        if len(pixel) == 4:
            pixel = pixel[:3]
        hex_color = '#{:02x}{:02x}{:02x}'.format(*pixel)
        self.state.fg_color = hex_color
        self.on_color_picked(hex_color)

    def on_drag(self, event):
        pass

    def on_release(self, event):
        pass
