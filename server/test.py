# Test.py - Tests and verifies usage of STG and PTS

from stg import SketchToGuess
from PIL import Image

stg = SketchToGuess()
img = Image.open('test_imgs/pizza.png')
guess = stg.guess(img)
print(guess)