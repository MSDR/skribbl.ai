from canvas import Canvas
from generative import generate_prompt, prompt_to_sketch, sketch_to_guess
import sys
import pygame
import ctypes
import random
import os

########## Pygame Setup #######################################################

# increase dots per inch so it looks sharper
ctypes.windll.shcore.SetProcessDpiAwareness(True)

# pygame config
pygame.init()
fps = 600
fpsClock = pygame.time.Clock()
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))

# canvas setup
canvas = Canvas()
canvasSize = 512 # canvas.canvasSize[0] is too verbose

# to track when mouse is released
mouse_pressed = False

# word stuff
current_word = "chef"

# fonts
hint_font = pygame.font.SysFont('Comic Sans', 40)


########## Game Loop #######################################################

while True:
    # background
    screen.fill((100, 100, 100))

    # process keyboard
    for event in pygame.event.get():
        # quit
        if (event.type == pygame.QUIT or 
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            sys.exit()

        # save & start new drawing
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT):
           canvas.reset()

        # undo
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_u):
            canvas.undo()

        # change color
        elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
            canvas.cycle_color()
        

    # draw canvas at the bottom-center of the screen
    canvas_coords = [canvasSize/2, screen_height/2 - canvasSize/2]
    screen.blit(canvas.canvas, canvas_coords)

    # draw current word at top of screen
    hint_surface = hint_font.render(current_word, True, [0,0,0])
    hint_rect = hint_surface.get_bounding_rect()
    screen.blit(hint_surface, (canvas_coords[0]+canvasSize/2-hint_rect.w/2, canvas_coords[1]-hint_rect.h*2))

    # draw when mouse is pressed
    if pygame.mouse.get_pressed()[0]:
        # calculate position on the canvas
        mx, my = pygame.mouse.get_pos()
        dx = mx - canvas_coords[0]
        dy = my - canvas_coords[1]

        canvas.draw_stroke(dx, dy)
        mouse_pressed = True

    else:
        # mouse just released, record canvas for undo
        if mouse_pressed:
            canvas.do()
            mouse_pressed = False

    # advance display
    pygame.display.flip()
    fpsClock.tick(fps)