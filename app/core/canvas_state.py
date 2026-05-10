"""Menyimpan semua state canvas: ukuran, zoom, daftar objek tergambar."""
from app.config import (
    CANVAS_DEFAULT_W, CANVAS_DEFAULT_H,
    DEFAULT_COLOR, DEFAULT_BG_COLOR,
    DEFAULT_WIDTH, DEFAULT_OPACITY,
    TOOL_LINE, LINE_STYLES
)


class CanvasState:
    def __init__(self):
        self.width  = CANVAS_DEFAULT_W
        self.height = CANVAS_DEFAULT_H
        self.zoom   = 100  # persen

        # Atribut drawing aktif
        self.active_tool    = TOOL_LINE
        self.fg_color       = DEFAULT_COLOR
        self.bg_color       = DEFAULT_BG_COLOR
        self.line_width     = DEFAULT_WIDTH
        self.opacity        = DEFAULT_OPACITY
        self.line_style     = "Solid"
        self.fill_shape     = False

        # Daftar semua objek yang sudah digambar
        # Format tiap item: dict {type, points, color, width, style, ...}
        self.objects: list = []

        # Objek yang sedang dipilih (untuk transform)
        self.selected_index: int = -1

        # Posisi kursor
        self.cursor_x = 0
        self.cursor_y = 0

    def add_object(self, obj: dict):
        self.objects.append(obj)

    def remove_object(self, index: int):
        if 0 <= index < len(self.objects):
            self.objects.pop(index)

    def clear(self):
        self.objects.clear()
        self.selected_index = -1

    def get_dash_pattern(self):
        return LINE_STYLES.get(self.line_style, ())

    def canvas_pixel_size(self):
        """Ukuran canvas dalam piksel layar sesuai zoom."""
        scale = self.zoom / 100
        return int(self.width * scale), int(self.height * scale)
