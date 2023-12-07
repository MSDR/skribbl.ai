## Test.py -- Tests and verifies functionality of ImgUtils module

from PIL import Image
from sketch import *

image = Image.open('test_imgs/pizza.png')
imgs = split_sketch_into_components(image)

# To see results
images = []
for img in imgs:
    images.append(cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGRA))
display_images(images)
