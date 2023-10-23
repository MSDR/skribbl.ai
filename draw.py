# starting point: https://thepythoncode.com/code/make-a-drawing-program-with-python

# Imports
import sys
import pygame
import ctypes
import random
import os

# Increase Dots Per inch so it looks sharper
ctypes.windll.shcore.SetProcessDpiAwareness(True)

# Pygame Configuration
pygame.init()
fps = 600
fpsClock = pygame.time.Clock()
width, height = 512, 540
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
font = pygame.font.SysFont('Arial', 20)

# Drawing Area Size
canvasSize = [512, 512]

# Brush Parameters
drawColor = [0, 0, 0]
brushSize = 8
brushSizeSteps = 12

words = []
with open("data/wordlist.txt", 'r') as file:
    for word in file:
        words.append(word.strip())

current_word = random.choice(words)

for word in words:
    folder_path = "data/drawings/"+word
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)

def save():
    pygame.image.save(canvas, "canvas.png")


# Canvas
canvas = pygame.Surface(canvasSize)
canvas.fill((255, 255, 255))

# Keep canvases for undo
prev_canvases = [canvas]
canvas = canvas.copy()
print(len(prev_canvases))
pressed = False

last_path = None

# Game loop.
while True:
    screen.fill((30, 30, 30))
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or 
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            sys.exit()
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT):
           # save drawing
           index = len([f for f in os.listdir("data/drawings/"+current_word)])
           last_path = "data/drawings/"+current_word+"/"+str(index)+".png"
           pygame.image.save(canvas, last_path)

           # prepare for next drawing
           current_word = random.choice(words)
           canvas.fill((255, 255, 255))
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_u and len(prev_canvases) > 1):
            prev_canvases.pop()
            canvas = prev_canvases[-1].copy()
            print(len(prev_canvases))
        elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_TAB and len(prev_canvases) > 1) and
              last_path is not None):
            os.remove(last_path)
            last_path = None
        
    # Draw the Canvas at the bottom of the screen
    x, y = screen.get_size()
    screen.blit(canvas, [x/2 - canvasSize[0]/2, y - canvasSize[1]])

    # Draw current word at top of screen
    word_surface = font.render(current_word, False, (255, 255, 255))
    screen.blit(word_surface, (x/2-word_surface.get_bounding_rect().w/2, 2))

    # Drawing with the mouse
    if pygame.mouse.get_pressed()[0]:
        pressed = True
        mx, my = pygame.mouse.get_pos()

        # Calculate Position on the Canvas
        dx = mx - x/2 + canvasSize[0]/2
        dy = my - y/2 + canvasSize[1]/2

        pygame.draw.circle(
            canvas,
            drawColor,
            [dx, dy],
            brushSize,
        )
    else:
        if pressed:
            prev_canvases.append(canvas)
            canvas = canvas.copy()
            pressed = False
            print(len(prev_canvases))

    pygame.display.flip()
    fpsClock.tick(fps)
