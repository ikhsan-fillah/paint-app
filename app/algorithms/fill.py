"""Flood fill algorithm."""


def flood_fill(pixels, x, y, target_color, replacement_color):
    if target_color == replacement_color:
        return
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cy < 0 or cx >= width or cy >= height:
            continue
        if pixels[cy][cx] != target_color:
            continue
        pixels[cy][cx] = replacement_color
        stack.extend([(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)])
