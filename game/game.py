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

import time

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
prompt_font = pygame.font.SysFont('Comic Sans', 40)
chat_font = pygame.font.SysFont('Comic Sans', 24)

# chat box
chat_box = ChatBox(chat_font)

# text box
def output_textbox():
    chat_box.chat("Human", textbox.getText())
    textbox.setText("")
textbox = TextBox(screen, 800, 578, 358, 40, font=chat_font,
                  borderColour=(0, 0, 0),
                  onSubmit=output_textbox, radius=2, borderThickness=4) 

# to track when mouse is released
currently_drawing = False

game_phase = "ai"

# word stuff
current_word = "full moon"
hint = None
hint_indices = []

round_start_time = int(time.time())


########## Game Functions ##################################################

def process_keyboard_events(events):
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

        elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_i)):
            canvas.draw_image(prompt_to_sketch("chef"))
            global round_start_time
            round_start_time = int(time.time())

def process_mouse_press():
    global currently_drawing
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()

        # draw if mouse pressed within canvas
        if (mx > canvas_coords[0] and mx < canvas_coords[0]+canvasSize and
            my > canvas_coords[1] and my < canvas_coords[1]+canvasSize):

            # calculate position on the canvas
            dx = mx - canvas_coords[0]
            dy = my - canvas_coords[1]

            canvas.draw_stroke(dx, dy)
            currently_drawing = True

    elif currently_drawing: # mouse just released from canvas
        canvas.do()
        currently_drawing = False

# this function isn't pretty but it works
def update_hint():
    global hint
    global hint_indices

    # update hint if necessary
    round_time = int(time.time())-round_start_time
    hint_count = max(int(round_time/15)-1, 0)
    if len(hint_indices) < hint_count:
        hint_indices.append(random.choice([i for i, c in enumerate(current_word) if i not in hint_indices and c != ' ']))

        # construct hint
        hint = "".join([c if i in hint_indices else ("-" if c != ' ' else ' ') for i, c in enumerate(current_word)])

    elif hint == None:
        hint = "".join([("-" if c != ' ' else ' ') for c in current_word])

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
def draw_prompt():
    # compute prompt
    update_hint()
    prompt = hint if game_phase != "human" else current_word

    # draw prompt
    prompt_surface = prompt_font.render('"'+prompt+'"', True, [0,0,0])
    prompt_rect = prompt_surface.get_bounding_rect()
    screen.blit(prompt_surface, (canvas_coords[0]+canvasSize/2-prompt_rect.w/2, canvas_coords[1]-60))

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

def draw_timer():
    # calculate timer interval
    round_time = int(time.time())-round_start_time
    timer_time = round_time - round_time%15 + (7 if round_time%15 >= 7 else 0)

    timer_image = pygame.image.load("game/assets/timer"+str(timer_time)+".png")
    screen.blit(timer_image, [1160, 0])


########## Game Loop ##########################################################

while True:
    # background color
    screen.fill((140, 200, 200))

    ### process keyboard events #######################
    events = pygame.event.get()
    process_keyboard_events(events)

    ### process mouse events ##########################
    process_mouse_press()

    ### draw elements to screen #######################
    draw_prompt()    # draw current word at top of screen
    draw_canvas()  # draw canvas at the bottom-center of the screen
    draw_chatbox() # draw chat box to the right of canvas
    draw_timer()

    ### advance display ###############################
    pygame_widgets.update(events)
    pygame.display.flip()
    fpsClock.tick(fps)