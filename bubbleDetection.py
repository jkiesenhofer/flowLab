import cv2
import numpy as np
import csv

# Load video
cap = cv2.VideoCapture("video.mp4")

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Video properties
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 30

# Video writer
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output.mp4", fourcc, fps, (width, height))

# CSV file
csv_file = open("bubbles.csv", mode="w", newline="")
csv_writer = csv.writer(csv_file)

# CSV header
csv_writer.writerow(["frame", "bubble_id", "x", "y", "radius"])

frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Grayscale + blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 1.5)

    # Detect bubbles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=30,
        param1=100,
        param2=30,
        minRadius=5,
        maxRadius=20
    )

    bubble_id = 0

    if circles is not None:
        circles = np.uint16(np.around(circles))

        for (x, y, r) in circles[0, :]:
            # Draw bubble
            cv2.circle(frame, (x, y), 50, (0, 255, 0), 2)
            cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)

            # Write to CSV
            csv_writer.writerow([frame_idx, bubble_id, x, y, r])

            bubble_id += 1

    # Write video frame
    out.write(frame)

    # Optional preview
    cv2.imshow("Bubble Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_idx += 1

# Cleanup
cap.release()
out.release()
csv_file.close()
cv2.destroyAllWindows()
