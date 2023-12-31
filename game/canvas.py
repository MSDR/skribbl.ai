import pygame
from PIL import Image

class Canvas():
    def __init__(self):
        # canvas parameters
        self.canvasSize = [512, 512]
        self.canvas = pygame.Surface(self.canvasSize)
        self.undo_history = []

        # brush parameters
        self.colors = [[0,0,0], [255,10,30], [30,255,90], [30,50,255], [120,60,30], [240, 240, 0]]
        self.erasing = False
        self.drawColor = 0
        self.brushSize = 8
        self.brushSizeSteps = 12

        # prep canvas & undo history
        self.reset()

    def reset(self):
        self.canvas.fill((255, 255, 255))
        self.drawColor = 0

        self.undo_history = []
        self.do()

    # appends current canvas to undo history
    def do(self):
        self.undo_history.append(self.canvas)
        self.canvas = self.canvas.copy()

    # undo (if there is something to undo)
    def undo(self):
        if len(self.undo_history) > 1:
            self.undo_history.pop()
            self.canvas = self.undo_history[-1].copy()

    # cycles through color list
    def cycle_color(self):
        self.drawColor += 1
        if self.drawColor >= len(self.colors):
            self.drawColor = 0

    # draws circle centered at x, y
    def draw_stroke(self, x, y):
        pygame.draw.circle(
            self.canvas,
            [255,255,255] if self.erasing else self.colors[self.drawColor],
            [x, y],
            self.brushSize,
        )

    def draw_image(self, image):
        image_bytes = image.tobytes()
        image_surface = pygame.image.fromstring(image_bytes, [512, 512], image.mode)
        self.canvas.blit(image_surface, [0,0])

    def get_image(self):
        pil_string = pygame.image.tostring(self.canvas, "RGB", False)
        return Image.frombytes("RGB", (512,512), pil_string)
