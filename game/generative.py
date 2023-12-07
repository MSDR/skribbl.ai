from PIL import Image
import pygame
import random

import base64
from io import BytesIO
import requests
from server.stg import SketchToGuess
from server.pts import PromptToSketch

class Generative():
    def __init__(self):
        self.stg = None#SketchToGuess()

    def generate_prompt(self):
        return random.choice(["chef", "apple", "tree", "worm", "pizza", "dog", "shark", "bridge", "slug", "parrot", "broccoli"])

    def prompt_to_sketch(self, prompt):
        #return pygame.image.load("game/chef.png")
        BASE_URL = "http://c1cc-128-113-60-117.ngrok-free.app/"
        url = f'{BASE_URL}/prompt_to_sketch'
        res = requests.get(url, params={'prompt': prompt})

        if res.status_code == 200:
            data = res.json()
            image_data = base64.b64decode(data['image'])
            image = Image.open(BytesIO(image_data))
            return image
        else:
            print("Unknown Error", res.json())

    def sketch_to_guess(self, image, hint=None):
        # if self.stg == None:
        #     return "placeholder"
        # return self.stg.guess(image, hint)

        BASE_URL = "http://127.0.0.1:5000"  # This will change
        sketch = image#Image.open('test_imgs/pizza.png')

        url = f'{BASE_URL}/sketch_to_guess'
        buffer = BytesIO()
        sketch.save(buffer, format='PNG')
        buffer.seek(0)
        res = requests.post(url, files={'file': ('anything.png', buffer, 'image/png')})

        if res.status_code == 200:
            data = res.json()
            guess = data['guess']
            return guess
        else:
            print("Unknown Error", res.json())