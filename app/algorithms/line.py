"""Algoritma pembentukan garis: DDA dan Bresenham (Midpoint)."""


def dda_line(x0, y0, x1, y1):
    """Digital Differential Analyzer — menggunakan float step."""
    points = []
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return [(x0, y0)]
    x_inc = dx / steps
    y_inc = dy / steps
    x, y = float(x0), float(y0)
    for _ in range(int(steps) + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc
    return points


def bresenham_line(x0, y0, x1, y1):
    """Bresenham Midpoint Line — hanya operasi integer, lebih efisien."""
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return points
