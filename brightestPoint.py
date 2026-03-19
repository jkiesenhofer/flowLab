import cv2
import csv
import time

cap = cv2.VideoCapture("coarseCollision.mp4")

with open("brightest_points.csv", "w", newline="") as f:
    writer = csv.writer(f)
    
    # header
    writer.writerow(["frame", "x", "y", "brightness"])

    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # find brightest pixel
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
        x, y = maxLoc
        time.sleep(0.2) 
        # write to CSV
        writer.writerow([frame_id, x, y, maxVal])
        # (optional) show it
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Brightest Point", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_id += 1

cap.release()
cv2.destroyAllWindows()
