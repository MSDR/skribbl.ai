# Test.py - Tests and verifies usage of STG and PTS

from stg import SketchToGuess
from pts import PromptToSketch
from PIL import Image

# Sketch To Guess Testing
stg = SketchToGuess()
img = Image.open('test_imgs/pizza.png')
guess = stg.guess(img)
print(guess)

# Prompt To Sketch Testing
pts = PromptToSketch()
img = pts.sketch('a pizza')
img.show()
