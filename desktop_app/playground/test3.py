import cv2
import numpy as np

# Initialize video capture
cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')

# Initialize the MOG2 background subtractor with parameters
mog2 = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)

# Define morphological operations kernels
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
small_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

# Set minimum object size threshold
min_object_area = 1000

# Process each frame with MOG2
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for faster processing
    frame = cv2.resize(frame, (640, 360))

    # Apply MOG2 background subtractor to get the foreground mask
    fg_mask = mog2.apply(frame)

    # Apply morphological operations to reduce noise
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

    # Apply erosion to remove small noise regions
    fg_mask = cv2.erode(fg_mask, small_kernel, iterations=1)

    # Apply a threshold to remove gray pixels (weak foreground regions)
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on minimum object area
    for contour in contours:
        if cv2.contourArea(contour) < min_object_area:
            continue

        # Get bounding box coordinates
        x, y, w, h = cv2.boundingRect(contour)

        # Draw bounding box on the original frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with bounding boxes
    cv2.imshow('Detected Objects', frame)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
