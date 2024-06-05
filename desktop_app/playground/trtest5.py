import cv2

# Initialize video capture
cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')

# Skip the first 100 frames
for _ in range(200):
    ret, _ = cap.read()
    if not ret:
        break

# Initialize the video frame
ret, frame = cap.read()
if not ret:
    exit()

# Initialize list to store selected ROIs and their corresponding trackers
selected_rois = []
trackers = []

# Function to create a new tracker with the selected ROI
def create_tracker(frame, roi):
    tracker = cv2.legacy.TrackerKCF_create()
    tracker.init(frame, roi)
    return tracker

# Function to draw bounding box on the frame
def draw_bbox(frame, bbox):
    x, y, w, h = [int(v) for v in bbox]
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Function to display the frame with bounding boxes
def display_frame(frame, bboxes):
    for bbox in bboxes:
        draw_bbox(frame, bbox)
    cv2.imshow('Tracking', frame)

# Select multiple ROIs
while True:
    bbox = cv2.selectROI('Select ROI', frame, fromCenter=False, showCrosshair=True)
    if bbox[2] > 0 and bbox[3] > 0:  # Check if a valid ROI is selected
        selected_rois.append(bbox)
        trackers.append(create_tracker(frame, bbox))
    else:
        break  # Exit selection loop if ROI selection is canceled

cv2.destroyWindow('Select ROI')

# Process each frame
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update each tracker and draw bounding boxes
    for i, tracker in enumerate(trackers):
        success, bbox = tracker.update(frame)
        if success:
            selected_rois[i] = bbox  # Update ROI in the list
            draw_bbox(frame, bbox)

    # Display the frame with bounding boxes
    display_frame(frame, selected_rois)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
