"""Algoritma pembentukan elips: Ellipse Midpoint (2 region)."""


def _ellipse_points(xc, yc, x, y):
    """Simetris 4 titik dari satu titik (x,y) terhadap pusat (xc,yc)."""
    return [
        (xc + x, yc + y), (xc - x, yc + y),
        (xc + x, yc - y), (xc - x, yc - y),
    ]


def midpoint_ellipse(xc, yc, rx, ry):
    """Ellipse Midpoint Algorithm — return list of (x,y) pixel positions."""
    points = []
    rx2 = rx * rx
    ry2 = ry * ry
    x, y = 0, ry

    # --- Region 1 ---
    p1 = ry2 - rx2 * ry + 0.25 * rx2
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y
    while dx < dy:
        points.extend(_ellipse_points(xc, yc, x, y))
        x += 1
        dx += 2 * ry2
        if p1 < 0:
            p1 += dx + ry2
        else:
            y -= 1
            dy -= 2 * rx2
            p1 += dx - dy + ry2

    # --- Region 2 ---
    p2 = (ry2 * (x + 0.5) ** 2
          + rx2 * (y - 1) ** 2
          - rx2 * ry2)
    while y >= 0:
        points.extend(_ellipse_points(xc, yc, x, y))
        y -= 1
        dy -= 2 * rx2
        if p2 > 0:
            p2 += rx2 - dy
        else:
            x += 1
            dx += 2 * ry2
            p2 += dx - dy + rx2
    return points
