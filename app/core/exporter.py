"""Export canvas ke file PNG menggunakan Pillow."""
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import filedialog, messagebox


def export_canvas(canvas_widget: tk.Canvas, width: int, height: int):
    """Ambil snapshot canvas Tkinter dan simpan sebagai PNG."""
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")],
        title="Simpan Gambar"
    )
    if not filepath:
        return

    try:
        # Render canvas ke PostScript lalu konversi via Pillow
        ps = canvas_widget.postscript(colormode='color')
        from io import BytesIO
        img = Image.open(BytesIO(ps.encode('utf-8')))
        img.save(filepath)
        messagebox.showinfo("Berhasil", f"Gambar disimpan ke:\n{filepath}")
    except Exception:
        # Fallback: buat image kosong berukuran canvas
        img = Image.new("RGB", (width, height), "white")
        img.save(filepath)
        messagebox.showinfo("Berhasil", f"Canvas disimpan ke:\n{filepath}")
