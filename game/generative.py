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
        self.local_url = "http://127.0.0.1:5000"
        self.server_url = "http://c1cc-128-113-60-117.ngrok-free.app/"

        self.prompts = []
        with open("game\\assets\\prompts.txt", 'r') as file:
            for word in file:
                self.prompts.append(word.strip())

        self.impressive_prompts = ["pirate", "pizza", "parrot", "smile", "wave", "house", "dog", "tree", "chef", "mushroom", "fish", "triangle", "circle", "square"]
        
    # returns a list of three prompt choices
    def sample_prompts(self):
        return random.sample(self.impressive_prompts, 3)

    def generate_prompt(self):
        url = f'{self.server_url}/choose_prompt'
        prompts = self.sample_prompts()
        # return prompts[0]
        res = requests.get(url, params={'prompts': prompts})

        if res.status_code == 200:
            prompt = res.json()['prompt']
            return prompt
        else:
            print("Unknown Error", res.json())

    def prompt_to_sketch(self, prompt):
        #return pygame.image.load("game/chef.png")
        url = f'{self.server_url}/prompt_to_sketch'
        res = requests.get(url, params={'prompt': prompt})

        if res.status_code == 200:
            data = res.json()
            image_data = base64.b64decode(data['image'])
            image = Image.open(BytesIO(image_data))
            return image
        else:
            print("Unknown Error", res.json())

    def sketch_to_guess(self, image, miss=None):
        # if self.stg == None:
        #     return "placeholder"
        # return self.stg.guess(image, hint)

        sketch = image#Image.open('test_imgs/pizza.png')

        url = f'{self.local_url}/sketch_to_guess'
        buffer = BytesIO()
        sketch.save(buffer, format='PNG')
        buffer.seek(0)
        if miss is None:
            res = requests.post(url, files={'file': ('anything.png', buffer, 'image/png')})
        else:
            res = requests.post(url, files={'file': ('anything.png', buffer, 'image/png')}, params={'miss': miss})

        if res.status_code == 200:
            data = res.json()
            guess = data['guess']
            return guess
        else:
            print("Unknown Error", res.json())