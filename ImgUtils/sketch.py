from io import BytesIO
from PIL import Image
import cv2
import numpy as np

def display(img):
    cv2.imshow('N/A', img)
    cv2.waitKey(0)

def display_images(imgs):
    canvas = np.full((imgs[0].shape[0], imgs[0].shape[1], 4), (255, 255, 255, 1), dtype=np.uint8)

    for img in imgs:
        # Copy only the A == 1 pixels to the canvas
        mask = img[:, :, 3] != 0
        canvas[mask] = img[mask]
        display(canvas)

def convert_to_png_in_memory(original_image):
    buffer = BytesIO()
    original_image.save(buffer, format='PNG')
    return Image.open(buffer)

def split_sketch_into_components(image: Image):
    # Make sure its the right format first
    image = convert_to_png_in_memory(image)

    # Convert PIL to OpenCV
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGRA)
    img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Remove background from simple mask 
    _, thres = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY_INV)
    mask = thres == 0
    replacement_value = np.array([255, 255, 255, 0], dtype=np.uint8)
    img_cv[mask] = replacement_value

    # Restrict to specific colors
    color_palette = np.array([[0, 0, 0, 1], [255, 10, 30, 1], [30, 255, 90, 1], [30, 50, 255, 1], [120, 60, 30, 1], [240, 240, 0, 1], [255, 255, 255, 1]])

    # Flatten the image into a 2D array of pixels
    pixels = img_cv.reshape(-1, 4)

    # Initialize an array to store the quantized colors
    quantized_colors = np.zeros_like(pixels)

    # For each pixel, find the nearest color in the predefined palette
    for i in range(len(pixels)):
        pixel = pixels[i]
        distances = np.linalg.norm(color_palette - pixel, axis=1)
        nearest_color_index = np.argmin(distances)
        quantized_colors[i] = color_palette[nearest_color_index]
    
    img_cv = quantized_colors.reshape(512, 512, 4)

    # Find contours, filter and sort them
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
    _, img_bw = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(img_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if 
                (cv2.contourArea(cnt) < (img_cv.shape[0] * img_cv.shape[1] * 0.95)) and 
                (cv2.contourArea(cnt) > 10)]
    contours = sorted(contours, key=lambda cnt: cv2.contourArea(cnt), reverse=False)
    imgs = []

    for i, cnt in enumerate(contours):
        # Create new transparent image
        transparent = np.zeros((img_cv.shape[0], img_cv.shape[1], 4), dtype=np.uint8)

        # Create a mask of the contours
        cv2.drawContours(transparent, contours, i, (1, 1, 1, 1), thickness=cv2.FILLED)
        new_img = transparent * img_cv
        imgs.append(new_img)

    # Incase we miss anything, pass the original image in as the last one
    imgs.append(img_cv)

    # Convert all of these to PIL images with RGBA values
    return [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)) for img in imgs] 