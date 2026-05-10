"""Basic transform helpers."""


def translate(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def scale(points, sx, sy):
    return [(int(x * sx), int(y * sy)) for x, y in points]
