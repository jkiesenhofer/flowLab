import cv2
import numpy as np

# Load image
image = cv2.imread("input.jpg")
output = image.copy()

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Blur to reduce noise (important for circle detection)
gray_blurred = cv2.GaussianBlur(gray, (9, 9), 1.5)

# Detect circles using Hough Transform
circles = cv2.HoughCircles(
    gray_blurred,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=50,
    param1=100,   # Canny edge threshold
    param2=30,    # Accumulator threshold (lower = more detections)
    minRadius=10,
    maxRadius=200
)

# Draw detected circles
if circles is not None:
    circles = np.uint16(np.around(circles))
    for (x, y, r) in circles[0, :]:
        # Draw outer circle
        cv2.circle(output, (x, y), r, (0, 255, 0), 2)
        # Draw center
        cv2.circle(output, (x, y), 2, (0, 0, 255), 3)

# Show results
cv2.imshow("Detected Bubbles", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
