from canvas import Canvas
from chat import ChatBox
from generative import generate_prompt, prompt_to_sketch, sketch_to_guess
import sys
import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
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
canvas_coords = [canvasSize/2, screen_height/2 - canvasSize/2] # [256, 104]

# fonts
hint_font = pygame.font.SysFont('Comic Sans', 40)
chat_font = pygame.font.SysFont('Comic Sans', 24)

# chat box
chat_box = ChatBox(chat_font)

# text box
def output_textbox():
    chat_box.chat("Human", textbox.getText())
    textbox.setText("")
textbox = TextBox(screen, 800, 578, 350, 40, font=chat_font,
                  borderColour=(0, 0, 0),
                  onSubmit=output_textbox, radius=2, borderThickness=4) 

# to track when mouse is released
mouse_pressed = False

# word stuff
current_word = "chef"


########## Display Functions ##################################################

# draw canvas at the bottom-center of the screen
def draw_canvas():
    screen.blit(canvas.canvas, canvas_coords)
    pygame.draw.rect(
        screen,
        [0,0,0],
        [canvas_coords[0]-2, canvas_coords[1]-2, canvasSize+4, canvasSize+4],
        4,
        2
    )

# draw current word at top of screen
def draw_hint():
    hint_surface = hint_font.render(current_word, True, [0,0,0])
    hint_rect = hint_surface.get_bounding_rect()
    screen.blit(hint_surface, (canvas_coords[0]+canvasSize/2-hint_rect.w/2, canvas_coords[1]-hint_rect.h*2))

# draw chat box to the right of canvas
def draw_chatbox():
    screen.blit(chat_box.surface, (804, 106))
    pygame.draw.rect(
        screen,
        [0,0,0],
        [800, 102, 358, 448],
        4,
        2
    )


########## Game Loop ##########################################################

while True:
    # background color
    screen.fill((100, 100, 100))

    ### process keyboard events #######################

    events = pygame.event.get()
    for event in events:
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

    ### process mouse events ##########################

    if pygame.mouse.get_pressed()[0]:
        # calculate position on the canvas
        mx, my = pygame.mouse.get_pos()

        # draw if mouse pressed within canvas
        if (mx > canvas_coords[0] and mx < canvas_coords[0]+canvasSize and
            my > canvas_coords[1] and my < canvas_coords[1]+canvasSize):

            dx = mx - canvas_coords[0]
            dy = my - canvas_coords[1]

            canvas.draw_stroke(dx, dy)
            mouse_pressed = True

    # mouse just released, record canvas for undo
    elif mouse_pressed:
        canvas.do()
        mouse_pressed = False

    ### draw elements to screen #######################

    # draw canvas at the bottom-center of the screen
    draw_canvas()

    # draw current word at top of screen
    draw_hint()

    # draw chat box to the right of canvas
    draw_chatbox()

    ### advance display ###############################
    pygame_widgets.update(events)
    pygame.display.flip()
    fpsClock.tick(fps)