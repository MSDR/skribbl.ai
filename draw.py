"""
Started from this template: https://thepythoncode.com/code/make-a-drawing-program-with-python
The script has been heavily modified from that template.

Instructions for use:
    LCLICK -> draw
    U      -> undo
    LSHIFT -> save and start new drawing
    TAB    -> delete previous drawing (in case of accidental save)
    ESC    -> quit

Drawings are 512x512 and saved to /data/drawings/[label]/

"""

########## Setup #######################################################

# imports
import sys
import pygame
import ctypes
import random
import os


# increase dots per inch so it looks sharper
ctypes.windll.shcore.SetProcessDpiAwareness(True)

# pygame config
pygame.init()
fps = 600
fpsClock = pygame.time.Clock()
width, height = 512, 540
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
font = pygame.font.SysFont('Arial', 20)

# define canvas
canvasSize = [512, 512]
canvas = pygame.Surface(canvasSize)
canvas.fill((255, 255, 255))

# brush parameters
drawColor = [0, 0, 0]
brushSize = 8
brushSizeSteps = 12


# load word choices
words = []
with open("data/wordlist.txt", 'r') as file:
    for word in file:
        words.append(word.strip())
current_word = random.choice(words)

# make save folders if needed
for word in words:
    folder_path = "data/drawings/"+word
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)


# keep canvases for undo
prev_canvases = [canvas]
canvas = canvas.copy()

# to track when mouse is released
mouse_pressed = False

# keep path of last image
last_image_path = "first"


########## Game Loop #######################################################

while True:
    # background
    screen.fill((30, 30, 30))

    # process keyboard
    for event in pygame.event.get():
        # quit
        if (event.type == pygame.QUIT or 
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            sys.exit()

        # save & start new drawing
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT):
           # save drawing
           index = len([f for f in os.listdir("data/drawings/"+current_word)])
           last_image_path = "data/drawings/"+current_word+"/"+str(index)+".png"
           pygame.image.save(canvas, last_image_path)

           # prepare for next drawing
           current_word = random.choice(words)
           canvas.fill((255, 255, 255))

        # undo
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_u and len(prev_canvases) > 1):
            prev_canvases.pop()
            canvas = prev_canvases[-1].copy()

        # delete previous drawing
        elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_TAB and len(prev_canvases) > 1) and
              last_image_path is not None and last_image_path != "first"):
            os.remove(last_image_path)
            last_image_path = None
        

    # draw canvas at the bottom-center of the screen
    x, y = screen.get_size()
    screen.blit(canvas, [x/2 - canvasSize[0]/2, y - canvasSize[1]])

    # draw current word at top of screen
    word_surface = font.render(current_word, False, (255, 255, 255))
    screen.blit(word_surface, (x/2-word_surface.get_bounding_rect().w/2, 2))

    # feedback for image deletion
    if last_image_path is None:
        word_surface = font.render("prev. image deleted", False, (255, 35, 35))
        screen.blit(word_surface, (4, 2))


    # draw when mouse is pressed
    if pygame.mouse.get_pressed()[0]:
        mouse_pressed = True
        mx, my = pygame.mouse.get_pos()

        # calculate position on the canvas
        dx = mx - x/2 + canvasSize[0]/2 - int(brushSize/2)
        dy = my - y/2 + canvasSize[1]/2 - int(brushSize/2)

        pygame.draw.circle(
            canvas,
            drawColor,
            [dx, dy],
            brushSize,
        )
    else:
        # mouse just released, record canvas for undo
        if mouse_pressed:
            prev_canvases.append(canvas)
            canvas = canvas.copy()
            mouse_pressed = False


    # advance display
    pygame.display.flip()
    fpsClock.tick(fps)