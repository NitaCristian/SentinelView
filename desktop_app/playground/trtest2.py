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

# Initialize list to store CSRT trackers
trackers = cv2.legacy.MultiTracker_create()

# Initialize the frame index
frame_index = 0

# Read the first few dummy frames
for _ in range(20):
    ret, frame = cap.read()
    if not ret:
        break

# Process each frame
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
    # fg_mask = cv2.erode(fg_mask, small_kernel, iterations=1)

    # Apply a threshold to remove gray pixels (weak foreground regions)
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Add new trackers for detected objects
    if frame_index % 5 == 0:  # Update every 5 frames
        new_trackers = cv2.legacy.MultiTracker_create()
        for contour in contours:
            if cv2.contourArea(contour) < min_object_area:
                continue

            # Apply watershed segmentation to separate closely located objects
            #mask = np.zeros_like(fg_mask)
            #cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
            #cv2.imshow('Mask', mask)
            #cv2.waitKey(1)
            #fg_mask = cv2.bitwise_and(fg_mask, mask)

            # Get bounding box coordinates
            x, y, w, h = cv2.boundingRect(contour)

            # Initialize a new CSRT tracker
            tracker = cv2.legacy.TrackerCSRT_create()
            new_trackers.add(tracker, frame, (x, y, w, h))

        trackers = new_trackers

    # Update all the trackers
    success, boxes = trackers.update(frame)
    for i, box in enumerate(boxes):
        x, y, w, h = [int(v) for v in box]

        # Draw bounding box on the original frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with bounding boxes
    cv2.imshow('Detected Objects', fg_mask)

    frame_index += 1
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
