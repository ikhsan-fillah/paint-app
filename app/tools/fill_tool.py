"""Tool paint bucket — flood fill pada canvas."""
from app.tools.base_tool import BaseTool
from PIL import Image, ImageTk
import tkinter as tk


class FillTool(BaseTool):
    def __init__(self, state, canvas, redraw_fn, get_pil_image_fn, set_pil_image_fn):
        super().__init__(state, canvas, redraw_fn)
        self.get_pil_image = get_pil_image_fn
        self.set_pil_image = set_pil_image_fn

    def on_press(self, event):
        x, y = event.x, event.y
        img = self.get_pil_image()
        if img is None or x >= img.width or y >= img.height:
            return
        fill_rgb = self._hex_to_rgb(self.state.fg_color)
        old_rgb = img.getpixel((x, y))
        if len(old_rgb) == 4:
            old_rgb = old_rgb[:3]
        if old_rgb == fill_rgb:
            return
        self._flood_fill_pil(img, x, y, fill_rgb, old_rgb)
        self.set_pil_image(img)
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

    @staticmethod
    def _hex_to_rgb(hex_color):
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
