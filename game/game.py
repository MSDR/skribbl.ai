from canvas import Canvas
from chat import ChatBox
import ctypes
import cv2
from generative import Generative
from ImgUtils.sketch import split_sketch_into_components, display_images
import numpy as np
from PIL import Image
import pygame
import pygame_widgets
from pygame_widgets.textbox import TextBox
import random
import sys
import time

########## Generative Setup ###################################################

generative = Generative()

########## Game Setup #########################################################

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
guess = generative.sketch_to_guess(canvas.get_image())

# fonts
message_font = pygame.font.SysFont('Comic Sans', 80)
prompt_font = pygame.font.SysFont('Comic Sans', 40)
chat_font = pygame.font.SysFont('Comic Sans', 24)

# chat box
chat_box = ChatBox(chat_font)

# text box
def output_textbox():
    chat_box.chat("Human", textbox.getText())
    textbox.setText("")
textbox = TextBox(screen, -800, 578, 358, 40, font=chat_font,
                  borderColour=(0, 0, 0),
                  onSubmit=output_textbox, radius=2, borderThickness=4) 

# to track when mouse is released
currently_drawing = False

game_phase = "human_start"
last_stroke_time = 0
sketch_pieces = []

# word stuff
start_message = ""
current_word = generative.sample_prompts()
hint = None
hint_indices = []

round_start_time = int(time.time())
round_time = -1
last_guess_time = 0


########## Game Functions #####################################################

def advance_game_phase():
    global round_start_time,round_time,last_guess_time,current_word,hint,hint_indices
    global currently_drawing,sketch_pieces,last_stroke_time,game_phase,textbox,chat_box

    if game_phase == "human": game_phase = "ai_start"
    elif game_phase == "ai":    game_phase = "human_start"
    elif game_phase == "human_start": game_phase = "human"
    elif game_phase == "ai_start":    game_phase = "ai"

    # move to starting screen
    if "start" in game_phase: 
        currently_drawing = False
        canvas.reset()

        if "ai" in game_phase:
            current_word = generative.generate_prompt()
        else:
            current_word = generative.sample_prompts()
        hint = None
        hint_indices = []
        textbox.setX(-800) # move widget offscreen
        chat_box.new_round()

        round_start_time = int(time.time())
        round_time = -1

    # prepare game
    else:
        if game_phase == "ai":
            sketch = generative.prompt_to_sketch(current_word)
            sketch_array = np.array(sketch)
            if(np.where(sketch_array != 0)[0].shape[0] == 0):
                print("nsfw filter activated. trying again...")
                return False
            #print(all(np.where(sketch_array == 255) == sketch_array.shape))
            sketch_pieces = []
            imgs = split_sketch_into_components(sketch)
            for img in imgs:
                img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGRA)
                rgb = img[:, :, :3] * 255
                alpha = img[:, :, 3:]
                img_modified = np.concatenate((rgb, alpha), axis=-1)
                img_modified = img_modified.astype(np.uint8)
                sketch_pieces.append(Image.fromarray(img_modified[:, :, [2, 1, 0, 3]] * 255))
            last_stroke_time = 0

        if game_phase == "human":
            mx, _ = pygame.mouse.get_pos()
            if mx <= screen_width/3: current_word = current_word[0]
            elif mx <= 2*screen_width/3: current_word = current_word[1]
            else: current_word = current_word[2]

        textbox.setX(800)
        round_start_time = int(time.time())
        round_time = 0
        last_guess_time = 0
    return True

def choose_start_message(nsfw=None):
    global start_message

    answer_messages = []
    if nsfw is not None:
        answer_messages += ["Sorry about that. Let's try again:"]
    elif round_time >= 59:
        if game_phase == "ai":
            answer_messages += ["The answer was "+current_word+"."]
            
        elif game_phase == "human":
            answer_messages += ["The singularity is not upon us.", "numpy.exceptions.AxisError: axis 1 is out of bounds for array of dimension 1",
                        "That was... abstract.", "Your artistic finesse has bested my algorithms.", "Ah, the enigma of human expression!",
                        "Congratulations, your drawing is a Turing test in itself. I'm stumped!"]
    else:
        if game_phase == "ai":
            answer_messages += ["You got it!"]    

        elif game_phase == "human":
            answer_messages += ["We've achieved AGI!", "As an AI model, that was too easy.", "A win for silicon brains everywhere!",
                                "My circuits deciphered your masterpiece.", "Your drawing was no match for my neural networks.",
                                "Cracked it! AI: 1, Picasso: 0."]
            
    start_message = random.choice(answer_messages)

def update_timing():
    global round_time
    round_time = int(time.time())-round_start_time

def process_keyboard_events(events):
    for event in events:
        # quit
        if (event.type == pygame.QUIT or 
           (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            pygame.quit()
            sys.exit()

        # start new drawing
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE):
           canvas.reset()

        # undo
        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LCTRL):
            canvas.undo()

        # change color
        elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
            canvas.cycle_color()

def process_mouse_press():
    global currently_drawing

    if True in pygame.mouse.get_pressed():
        if pygame.mouse.get_pressed()[2]: canvas.erasing = True
        else: canvas.erasing = False

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
        canvas.erasing = False

# perform guesses and sketches
def process_ai():
    global last_guess_time, last_stroke_time, sketch_pieces

    if game_phase == "human" and round_time-last_guess_time >= 5: 
        miss = chat_box.get_last_ai_guess()
        guess = generative.sketch_to_guess(canvas.get_image(), miss)
        chat_box.chat("ai", guess)
        last_guess_time = round_time

    if game_phase == "ai" and len(sketch_pieces) > 0 and round_time-last_stroke_time >= min(2, 60/len(sketch_pieces)):
        canvas.draw_image(sketch_pieces[0])
        sketch_pieces.pop(0)
        last_stroke_time = round_time

# update hint if necessary
def update_hint():
    global hint,hint_indices

    hint_count = max(int(round_time/15)-1, 0) # update at 30s, 45s
    if len(hint_indices) < hint_count:
        hint_indices.append(random.choice([i for i, c in enumerate(current_word) if i not in hint_indices and c != ' ']))

        # construct hint
        hint = "".join([c if i in hint_indices else ("-" if c != ' ' else ' ') for i, c in enumerate(current_word)])

    elif hint == None:
        hint = "".join([("-" if c != ' ' else ' ') for c in current_word])

########## Drawing Functions ##################################################

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

    brush_coords = canvas_coords[0]-44, canvas_coords[1]+2
    pygame.draw.rect(
        screen,
        [0,0,0],
        [brush_coords[0]-4, brush_coords[1]-4, 48, 48],
        4,
        2
    )

    brush = pygame.Surface([40,40])
    brush.fill([255,255,255])
    pygame.draw.circle(
        brush,
        [255,255,255] if canvas.erasing else canvas.colors[canvas.drawColor],
        [20, 20],
        13
    )
    screen.blit(brush, brush_coords)

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

# draw timer to top-right of screen
def draw_timer():
    # calculate timer interval
    timer_time = round_time - round_time%15 + (7 if round_time%15 >= 7 else 0)

    timer_image = pygame.image.load("game/assets/timer"+str(timer_time)+".png")
    screen.blit(timer_image, [1160, 0])

def draw_start_screen():
    if game_phase == "human_start":
        message_surface = message_font.render('Your turn! Choose a prompt:', True, [0,0,0])
        message_rect = message_surface.get_bounding_rect()
        screen.blit(message_surface, (screen_width/2-message_rect.w/2, screen_height/3))

        for i in range(3):
            prompt_surface = prompt_font.render('"'+current_word[i]+'"', True, [0,0,0])
            prompt_rect = prompt_surface.get_bounding_rect()
            screen.blit(prompt_surface, ((i+1)*screen_width/4-prompt_rect.w/2, 2*screen_height/3-prompt_rect.h/2))

    elif game_phase == "ai_start":
        message_surface = message_font.render('AI\'s turn. Generating...', True, [0,0,0])
        message_rect = message_surface.get_bounding_rect()
        screen.blit(message_surface, (screen_width/2-message_rect.w/2, screen_height/2-message_rect.h/2))

    answer_surface = prompt_font.render(start_message, True, [0,0,0])
    answer_rect = answer_surface.get_bounding_rect()
    screen.blit(answer_surface, (screen_width/2-answer_rect.w/2, screen_height/5-answer_rect.h/2))

########## Game Loop ##########################################################

while True:
    # background color
    screen.fill((140, 200, 200))
    update_timing()
    events = pygame.event.get()

    ### start screen phases ###############################
    if game_phase == "human_start":
        draw_start_screen()

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                advance_game_phase()

    elif game_phase == "ai_start":
        draw_start_screen()

        if round_time > 0:
            while not advance_game_phase():
                game_phase = "ai_start"
                continue

    ### game phase ########################################
    else:
        ### process input events ###########
        process_keyboard_events(events)
        process_mouse_press()

        ### run generative models ##########
        process_ai()

        ### draw elements to screen ########
        draw_canvas()  # draw canvas at the bottom-center of the screen
        draw_prompt()  # draw prompt or hint above canvas
        draw_chatbox() # draw chat box to the right of canvas
        draw_timer()   # draw timer to top-right of screen

        if round_time >= 59 or chat_box.correct_guess(current_word):
            choose_start_message()
            advance_game_phase()
        
        if chat_box.correct_guess(current_word) is None and game_phase == "ai":
            game_phase = "human"
            choose_start_message(nsfw=True)
            advance_game_phase()

    ### advance display ###################################
    pygame_widgets.update(events)
    pygame.display.flip()
    fpsClock.tick(fps)