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

def split_sketch_into_components(image: Image):
    # Convert PIL to OpenCV
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGRA)
    img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    # Remove background from simple mask 
    _, thres = cv2.threshold(img_gray, 165, 255, cv2.THRESH_BINARY_INV)
    mask = thres == 0
    replacement_value = np.array([255, 255, 255, 0], dtype=np.uint8)
    img_cv[mask] = replacement_value

    # Find contours, filter and sort them
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

    # To see results
    # display_images(imgs)

    # Convert all of these to PIL images with RGBA values
    return [Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)) for img in imgs] 