import cv2
import numpy as np

# Step 1: Load the image
image = cv2.imread('input.jpg')  # Replace with your image file path

# Step 2: Convert to grayscale (brightness is easier to handle in a single channel)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Step 3: Find the brightest point
(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

print(f"Brightest value: {maxVal} at position {maxLoc}")

# Step 4: Draw a circle on the brightest point
result = image.copy()
cv2.circle(result, maxLoc, 10, (0, 0, 255), 2)  # Red circle

# Step 5: Display the result
cv2.imshow("Brightest Point", result)
cv2.waitKey(0)
cv2.destroyAllWindows()