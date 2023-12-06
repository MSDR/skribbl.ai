from PIL import Image
import pygame
import random

def generate_prompt():
    return random.choice(["chef", "flower", "apple"])

def prompt_to_sketch(prompt):
    return pygame.image.load("game/chef.png")

def sketch_to_guess(image):
    return "chef"