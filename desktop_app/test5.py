import cv2
import numpy as np

# Load video
cap = cv2.VideoCapture('./files/Traffic_Laramie_1.mp4')

# Initialize Mean Shift parameters
mean_shift_params = {'window_size': (30, 30), 'criteria': (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)}

# Read the first frame
ret, frame = cap.read()
if not ret:
    print("Error: Failed to read video")
    exit()

for _ in range(50):
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read video")
        exit()

# Select initial tracking window (region of interest)
x, y, w, h = 900, 490, 100, 50  # Example initial window coordinates
roi = frame[y:y + h, x:x + w]

# Convert ROI to HSV
hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# Calculate histogram of ROI
roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])

# Normalize histogram
roi_hist = cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

# Initialize tracking window
track_window = (x, y, w, h)

# Initialize CamShift parameters
term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)



while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform Mean Shift to get new location
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)
    ret, track_window = cv2.meanShift(dst, track_window, term_crit)

    # Draw new window
    x, y, w, h = track_window
    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('MeanShift Tracking', frame)
    #cv2.waitKey()
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
