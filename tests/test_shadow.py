import cv2
import numpy as np
from PIL import Image, ImageDraw

def show_img(img):
    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.imshow('img', img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def create_rounded_rect_mask(size, radius):
    """
    Create a mask with a rounded rectangle.
    """
    width, height = size
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)
    return np.array(mask)

def make_blurry_shadow(image, border, offset, shadow_color, blur_radius):
    """
    Create a blurry shadow for an image.
    """
    # Calculate the size of the shadow's image
    full_width = image.shape[1] + abs(offset[0]) + 2 * border
    full_height = image.shape[0] + abs(offset[1]) + 2 * border

    # Create the shadow's image with an alpha channel
    shadow = np.zeros((full_height, full_width, 4), dtype=np.uint8)

    # Place the shadow, with the required offset
    shadow_left = border + max(offset[0], 0)  # if <0, push the rest of the image right
    shadow_top = border + max(offset[1], 0)  # if <0, push the rest of the image down

    # Create a mask for the rounded rectangle
    mask = create_rounded_rect_mask((image.shape[1], image.shape[0]), 16)

    # Add shadow color to the mask
    shadow[shadow_top:shadow_top + image.shape[0], shadow_left:shadow_left + image.shape[1]][mask == 255] = (*shadow_color, 255)

    # Apply Gaussian blur to the shadow
    shadow = cv2.GaussianBlur(shadow, (0, 0), blur_radius)
    show_img(shadow)

    return shadow

def add_image_with_shadow(base_image, shadow_image, image, border, offset):
    """
    Add the base image on top of the shadow.
    """
    # Ensure base_image has an alpha channel
    if base_image.shape[2] == 3:
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2BGRA)

    # Combine the base image with the shadow
    overlay = base_image.copy()
    overlay[0:shadow_image.shape[0], 0:shadow_image.shape[1]] = shadow_image

    # Blend the shadow with the base image
    base_image = cv2.addWeighted(overlay, 1, base_image, 1, 0)

    # Position the original image on top of the shadow
    img_left = border - min(offset[0], 0)  # if the shadow offset was <0, push right
    img_top = border - min(offset[1], 0)  # if the shadow offset was <0, push down

    # Ensure the original image has an alpha channel
    if image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    base_image[img_top:img_top + image.shape[0], img_left:img_left + image.shape[1]] = image

    return base_image

if __name__ == "__main__":
    # Load the image
    image_path = "test.png"  # Replace with your image file path
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    # Image parameters
    border = 100
    shadow_color = (0, 0, 0)  # Shadow color without transparency
    blur_radius = 20
    offset = (0, 0)  # Shadow offset

    # Create the base image with a white background
    base_image_path = '/home/tamnv/Downloads/google-deepmind-ryxY5haw8xg-unsplash.jpg'  # Replace with your base image file path
    base_image = cv2.imread(base_image_path, cv2.IMREAD_UNCHANGED)

    # Ensure the base image has an alpha channel
    if base_image.shape[2] == 3:
        base_image = cv2.cvtColor(base_image, cv2.COLOR_BGR2BGRA)

    # Create the blurry shadow
    shadow_image = make_blurry_shadow(image, border, offset, shadow_color, blur_radius)

    # Combine the base image with the shadow and the original image
    result_image = add_image_with_shadow(base_image, shadow_image, image, border, offset)

    # Show the result
    show_img(result_image)
    cv2.destroyAllWindows()
