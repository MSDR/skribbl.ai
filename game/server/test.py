# Test.py - Tests and verifies usage of STG and PTS

import base64
from io import BytesIO
import requests
# from stg import SketchToGuess
# from pts import PromptToSketch
from PIL import Image

# # Sketch To Guess Testing
# stg = SketchToGuess()
# img = Image.open('test_imgs/pizza.png')
# guess = stg.guess(img)
# print(guess)

# # Prompt To Sketch Testing
# pts = PromptToSketch()
# img = pts.sketch('a pizza')
# img.show()

# Prompt To Prompt GET Testing
BASE_URL = "http://127.0.0.1:5000"  # This will change
prompts = ['pizza', 'apple', 'house']

url = f'{BASE_URL}/choose_prompt'
res = requests.get(url, params={'prompts': prompts})

if res.status_code == 200:
    prompt = res.json()['prompt']
    print(prompt)
else:
    print("Unknown Error", res.json())

# Prompt To Sketch GET Testing
BASE_URL = "http://127.0.0.1:5000"  # This will change
prompt = "a pizza"

url = f'{BASE_URL}/prompt_to_sketch'
res = requests.get(url, params={'prompt': prompt})

if res.status_code == 200:
    data = res.json()
    image_data = base64.b64decode(data['image'])
    image = Image.open(BytesIO(image_data))
    image.show()
else:
    print("Unknown Error", res.json())

# Sketch To Guess POST Testing
BASE_URL = "http://127.0.0.1:5000"  # This will change
sketch = Image.open('test_imgs/pizza.png')

url = f'{BASE_URL}/sketch_to_guess'
buffer = BytesIO()
sketch.save(buffer, format='PNG')
buffer.seek(0)
res = requests.post(url, files={'file': ('anything.png', buffer, 'image/png')})

if res.status_code == 200:
    data = res.json()
    guess = data['guess']
    print(guess)
else:
    print("Unknown Error", res.json())