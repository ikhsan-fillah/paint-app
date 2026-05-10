"""Abstract base class untuk semua tool."""
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Setiap tool harus mengimplementasikan ketiga method ini."""

    def __init__(self, state, canvas, redraw_fn):
        """
        state      : CanvasState
        canvas     : tk.Canvas widget
        redraw_fn  : callable — panggil untuk refresh tampilan canvas
        """
        self.state = state
        self.canvas = canvas
        self.redraw = redraw_fn

        # Titik awal klik
        self.start_x = 0
        self.start_y = 0

        # ID preview sementara di canvas Tkinter
        self._preview_id = None

    def on_press(self, event):
        """Mouse button ditekan."""
        self.start_x = event.x
        self.start_y = event.y

    @abstractmethod
    def on_drag(self, event):
        """Mouse digeser sambil tombol ditekan."""
        pass

    @abstractmethod
    def on_release(self, event):
        """Mouse button dilepas — finalisasi objek."""
        pass

    def on_double_click(self, event):
        """Override jika tool membutuhkan double-click (misal polygon)."""
        pass

    def _clear_preview(self):
        if self._preview_id is not None:
            try:
                self.canvas.delete(self._preview_id)
            except Exception:
                pass
            self._preview_id = None
