"""Algoritma pengisian area: Boundary-Fill dan Flood-Fill (4-connected)."""
from collections import deque


def boundary_fill_4(get_pixel, set_pixel, x, y, fill_color, boundary_color, width, height):
    """
    Boundary-Fill 4-connected.
    get_pixel(x,y) -> color tuple
    set_pixel(x,y, color)
    """
    queue = deque()
    queue.append((x, y))
    visited = set()
    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        current = get_pixel(cx, cy)
        if current == boundary_color or current == fill_color:
            continue
        set_pixel(cx, cy, fill_color)
        visited.add((cx, cy))
        queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])


def flood_fill_4(get_pixel, set_pixel, x, y, fill_color, width, height):
    """
    Flood-Fill 4-connected — ganti semua piksel warna lama dengan warna baru.
    """
    old_color = get_pixel(x, y)
    if old_color == fill_color:
        return
    queue = deque()
    queue.append((x, y))
    visited = set()
    while queue:
        cx, cy = queue.popleft()
        if (cx, cy) in visited:
            continue
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        if get_pixel(cx, cy) != old_color:
            continue
        set_pixel(cx, cy, fill_color)
        visited.add((cx, cy))
        queue.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
