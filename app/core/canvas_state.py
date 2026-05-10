"""Canvas state model."""


class CanvasState:
    def __init__(self, width, height, background=(255, 255, 255)):
        self.width = width
        self.height = height
        self.background = background
        self.pixels = [[background for _ in range(width)] for _ in range(height)]

    def clear(self):
        for y in range(self.height):
            for x in range(self.width):
                self.pixels[y][x] = self.background
