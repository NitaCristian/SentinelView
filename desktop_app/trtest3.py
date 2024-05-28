import cv2

# Initialize video capture
cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')

# Initialize the MOG2 background subtractor with parameters
mog2 = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)

# Define morphological operations kernels
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
small_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

# Set minimum object size threshold
min_object_area = 1000

# Initialize list to store CSRT trackers and their corresponding bounding boxes
trackers = []
bounding_boxes = []

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
    fg_mask = cv2.erode(fg_mask, small_kernel, iterations=1)

    # Apply a threshold to remove gray pixels (weak foreground regions)
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Update existing trackers with new bounding boxes
    for contour in contours:
        if cv2.contourArea(contour) < min_object_area:
            continue

        # Get bounding box coordinates
        x, y, w, h = cv2.boundingRect(contour)

        # Check if the bounding box is near any existing trackers
        is_near_existing_tracker = False
        for box in bounding_boxes:
            x_center, y_center = box[0] + box[2] // 2, box[1] + box[3] // 2
            new_x_center, new_y_center = x + w // 2, y + h // 2
            distance = ((x_center - new_x_center) ** 2 + (y_center - new_y_center) ** 2) ** 0.5
            if distance < 50:
                is_near_existing_tracker = True
                break

        if not is_near_existing_tracker:
            # Initialize a new CSRT tracker
            tracker = cv2.legacy.TrackerCSRT_create()
            trackers.append(tracker)
            bounding_boxes.append((x, y, w, h))

    # Update all the trackers
    for i, tracker in enumerate(trackers):
        success, box = tracker.update(frame)
        if success:
            bounding_boxes[i] = (int(box[0]), int(box[1]), int(box[2]), int(box[3]))
        else:
            # If tracking fails, remove the tracker and bounding box
            del trackers[i]
            del bounding_boxes[i]

    # Draw bounding boxes on the original frame
    for box in bounding_boxes:
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame with bounding boxes
    cv2.imshow('Detected Objects', frame)

    frame_index += 1
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
