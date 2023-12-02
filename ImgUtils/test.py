## Test.py -- Tests and verifies functionality of ImgUtils module

from PIL import Image
from sketch import *

image = Image.open('test_imgs/tree.png')
imgs = split_sketch_into_components(image)