import cv2
import numpy as np
from scipy.spatial import distance

# --- PARAMETERS ---
MAX_DISTANCE = 50  # max distance to consider same bubble

# --- TRACKING STATE ---
next_bubble_id = 0
tracked_bubbles = {}  # id -> centroid


def get_centroid(contour):
    M = cv2.moments(contour)
    if M["m00"] == 0:
        return None
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return (cx, cy)


def detect_bubbles(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)

    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        11, 2
    )

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    bubbles = []
    for cnt in contours:
        area = cv2.contourArea(cnt)

        # Filter noise
        if area < 100:
            continue

        centroid = get_centroid(cnt)
        if centroid:
            bubbles.append((centroid, cnt))

    return bubbles


def match_bubbles(prev, current):
    global next_bubble_id

    new_tracked = {}
    used_current = set()

    prev_ids = list(prev.keys())
    prev_centroids = list(prev.values())
    current_centroids = [c[0] for c in current]

    if len(prev_centroids) > 0 and len(current_centroids) > 0:
        D = distance.cdist(prev_centroids, current_centroids)

        for i in range(len(prev_centroids)):
            min_idx = np.argmin(D[i])

            if D[i][min_idx] < MAX_DISTANCE and min_idx not in used_current:
                bubble_id = prev_ids[i]
                new_tracked[bubble_id] = current_centroids[min_idx]
                used_current.add(min_idx)

    # Assign new IDs
    for i, (centroid, _) in enumerate(current):
        if i not in used_current:
            new_tracked[next_bubble_id] = centroid
            next_bubble_id += 1

    return new_tracked


# --- MAIN ---
cap = cv2.VideoCapture("suspension.mp4")

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0:
    fps = 30  # fallback

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Setup output video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output.mp4", fourcc, int(fps), (width, height))

print("VideoWriter opened:", out.isOpened())

while True:
    ret, frame = cap.read()
    if not ret:
        break

    bubbles = detect_bubbles(frame)
    tracked_bubbles = match_bubbles(tracked_bubbles, bubbles)

    # Draw results
    for bubble_id, centroid in tracked_bubbles.items():
        cv2.putText(
            frame,
            f"ID {bubble_id}",
            centroid,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )
        cv2.circle(frame, centroid, 5, (0, 0, 255), -1)

    # Save frame
    out.write(frame)

    # Show frame
    cv2.imshow("Bubble Tracking", frame)

    if cv2.waitKey(30) & 0xFF == 27:
        break

# Cleanup
cap.release()
out.release()
cv2.destroyAllWindows()
