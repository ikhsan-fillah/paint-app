"""Algoritma pembentukan lingkaran: Circle Midpoint (Bresenham)."""


def _circle_points(xc, yc, x, y):
    """Simetris 8 titik dari satu titik (x,y) terhadap pusat (xc,yc)."""
    return [
        (xc + x, yc + y), (xc - x, yc + y),
        (xc + x, yc - y), (xc - x, yc - y),
        (xc + y, yc + x), (xc - y, yc + x),
        (xc + y, yc - x), (xc - y, yc - x),
    ]


def midpoint_circle(xc, yc, r):
    """Circle Midpoint Algorithm — return list of (x,y) pixel positions."""
    points = []
    x, y = 0, r
    p = 1 - r
    points.extend(_circle_points(xc, yc, x, y))
    while x < y:
        x += 1
        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * x - 2 * y + 1
        points.extend(_circle_points(xc, yc, x, y))
    return points
