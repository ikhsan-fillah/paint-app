"""Ellipse drawing algorithms."""


def midpoint_ellipse(cx, cy, rx, ry):
    points = []
    x = 0
    y = ry
    rx2 = rx * rx
    ry2 = ry * ry
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    p1 = ry2 - (rx2 * ry) + (0.25 * rx2)
    while dx < dy:
        points.extend([
            (cx + x, cy + y),
            (cx - x, cy + y),
            (cx + x, cy - y),
            (cx - x, cy - y),
        ])
        x += 1
        dx = 2 * ry2 * x
        if p1 < 0:
            p1 += ry2 + dx
        else:
            y -= 1
            dy = 2 * rx2 * y
            p1 += ry2 + dx - dy

    p2 = (ry2 * ((x + 0.5) ** 2)) + (rx2 * ((y - 1) ** 2)) - (rx2 * ry2)
    while y >= 0:
        points.extend([
            (cx + x, cy + y),
            (cx - x, cy + y),
            (cx + x, cy - y),
            (cx - x, cy - y),
        ])
        y -= 1
        dy = 2 * rx2 * y
        if p2 > 0:
            p2 += rx2 - dy
        else:
            x += 1
            dx = 2 * ry2 * x
            p2 += rx2 - dy + dx
    return points
