import cv2
import numpy as np
import csv
import math

# Load video
cap = cv2.VideoCapture("bubbles.avi")

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

# CSV file setup
csv_file = open("bubbles.csv", mode="w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["frame", "bubble_id", "center_x", "center_y", "axes_major", "axes_minor", "angle", "vx", "vy", "speed_magnitude"])

frame_idx = 0
next_bubble_id = 0

# Dictionary to track bubbles from the PREVIOUS frame: { bubble_id: (x, y) }
prev_bubbles = {}

# Max distance (pixels) a bubble can travel between frames to keep its ID
MAX_TRACKING_DISTANCE = 40 

while True:
    ret, frame = cap.read()
    if not ret:
        print("Processing finished.")
        break

    # 1. Image Preprocessing for Contour Detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Thresholding to separate bubbles from background 
    # (Adjust threshold values 50, 255 based on your lighting conditions)
    _, thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 2. Find Contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_bubbles = {}

    for contour in contours:
        # Ignore tiny noise artifacts or massive objects
        area = cv2.contourArea(contour)
        if area < 50 or area > 5000:
            continue

        # cv2.fitEllipse requires at least 5 points to construct a valid ellipse
        if len(contour) < 5:
            continue

        # 3. Fit Ellipse
        # ellipse structure: ((center_x, center_y), (axes_major, axes_minor), rotation_angle)
        ellipse = cv2.fitEllipse(contour)
        (x, y), (ma, mi), angle = ellipse
        x, y = int(x), int(y)

        # 4. Tracking / ID Assignment via Euclidean Distance
        matched_id = None
        min_dist = MAX_TRACKING_DISTANCE

        for prev_id, (prev_x, prev_y) in prev_bubbles.items():
            dist = math.hypot(x - prev_x, y - prev_y)
            if dist < min_dist:
                min_dist = dist
                matched_id = prev_id

        if matched_id is None:
            matched_id = next_bubble_id
            next_bubble_id += 1

        # 5. Calculate Velocity and Magnitude
        vx, vy = 0, 0
        magnitude = 0.0
        
        if matched_id in prev_bubbles:
            prev_x, prev_y = prev_bubbles[matched_id]
            vx = int(x - prev_x)
            vy = int(y - prev_y)
            magnitude = math.hypot(vx, vy)  

        current_bubbles[matched_id] = (x, y)

        # --- Visualization Layer ---
        # Draw the Ellipsoidal shape (Green)
        cv2.ellipse(frame, ellipse, (0, 255, 0), 2)
        
        # Render Bubble ID label just above the ellipse center
        cv2.putText(frame, f"ID:{matched_id}", (x + 12, y - 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
        
        # Draw the Vector Arrow and print the Magnitude
        scale = 2 
        arrow_end_x = int(x + vx * scale)
        arrow_end_y = int(y + vy * scale)
        
        if vx != 0 or vy != 0:
            # Draw blue velocity tracking arrow
            cv2.arrowedLine(frame, (x, y), (arrow_end_x, arrow_end_y), (255, 0, 0), 2, tipLength=0.3)
            
            # Print velocity magnitude (speed) right at the tip of the arrow
            cv2.putText(frame, f"{magnitude:.1f} px/f", (arrow_end_x + 5, arrow_end_y + 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

        # Write dataset row to CSV
        csv_writer.writerow([frame_idx, matched_id, x, y, round(ma, 2), round(mi, 2), round(angle, 2), vx, vy, round(magnitude, 2)])

    # Pass tracking data to cache for next frame
    prev_bubbles = current_bubbles

    # Write output video frame
    out.write(frame)

    # UI Preview Window
    cv2.imshow("Ellipsoidal Bubble Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Interrupted by user.")
        break

    frame_idx += 1

# Cleanup operations
cap.release()
out.release()
csv_file.close()
cv2.destroyAllWindows()
