import cv2
import numpy as np
from PIL import Image
import pygame
from rembg import remove


# Step 1: Load and reshape the image
def load_and_reshape_image(filepath, new_size=(300, 300)):
    # Load with Pillow
    img = Image.open(filepath)
    # Reshape (resize)
    img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
    # Convert to OpenCV format (numpy array)
    img_array = np.array(img_resized)
    return img_array

def show_image(img, window_name="Image"):
    cv2.imshow(window_name, img)  # Display the image
    cv2.waitKey(0)  # Wait for any key press
    cv2.destroyAllWindows()  # Close the window

# Step 3: Save image to path
def save_image(img, output_path):
    cv2.imwrite(output_path, img)  # Write image to file
    print(f"Image saved to {output_path}")
# Step 2: Simplify image to vector-like style
# Step 2: Remove white background
def remove_white_background(input_path,output_path):
    img = Image.open(input_path).convert("RGBA")
    img= img.resize((512,512), Image.Resampling.LANCZOS)
    datas = img.getdata()

    new_data = []
    for pixel in datas:
        # pixel is in RGBA format (R, G, B, A)
        # Adjust threshold as needed for near-white
        if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:
            # Replace with transparent
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(pixel)

    # Update image data and save
    img.putdata(new_data)
    img.save(output_path, "PNG")

    print("Background removed. Saved to", output_path)


# Step 3: Vectorize the image
def vectorize_image(img, mask):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Use the mask to focus on the dragon
    gray = cv2.bitwise_and(gray, gray, mask=mask)

    # Apply edge detection
    edges = cv2.Canny(gray, 100, 200)
    # Dilate edges to make them bolder
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a blank image for vectorized output
    vector_img = np.zeros_like(img)
    # Draw contours (white lines for vector effect)
    cv2.drawContours(vector_img, contours, -1, (255, 255, 255), 2)

    return vector_img
if __name__ == "__main__":
    # img=load_and_reshape_image("../graphics/character/down/down0.jpeg")
    # img,mask=remove_white_background(img)
    filepath="../graphics/character/down/test.png"
    outpath="../graphics/character/down/test_vector.png"
    remove_white_background(filepath,outpath)
    #img=vectorize_image(img,mask)
    #show_image(img)