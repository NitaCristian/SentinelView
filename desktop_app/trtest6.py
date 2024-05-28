import cv2


# Function to calculate overlap percentage between two bounding boxes
def calculate_overlap(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    # Calculate the coordinates of the intersection rectangle
    x_intersection = max(x1, x2)
    y_intersection = max(y1, y2)
    w_intersection = min(x1 + w1, x2 + w2) - x_intersection
    h_intersection = min(y1 + h1, y2 + h2) - y_intersection

    # Calculate the areas of the bounding boxes and the intersection
    area1 = w1 * h1
    area2 = w2 * h2
    area_intersection = max(0, w_intersection) * max(0, h_intersection)

    # Calculate the overlap percentage
    overlap_percentage = area_intersection / min(area1, area2)

    return overlap_percentage


# Initialize video capture and tracker
cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')
tracker = cv2.legacy.TrackerCSRT_create()

# Skip the first few frames
for _ in range(100):
    cap.read()

# Read the first frame
ret, frame = cap.read()
if not ret:
    exit()

# Select ROI
bbox = cv2.selectROI('Select ROI', frame, fromCenter=False, showCrosshair=True)
cv2.destroyWindow('Select ROI')

# Initialize the tracker with the selected ROI
tracker.init(frame, bbox)

# Parameters for tracking failure detection
overlap_threshold = 0.5  # Threshold for overlap percentage
appearance_threshold = 0.8  # Threshold for appearance similarity score
prev_bbox = bbox  # Initialize previous bounding box

# Process each frame
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update the tracker
    success, bbox = tracker.update(frame)
    if not success:
        print("Tracking failure detected")
        break

    # Calculate overlap with background
    overlap_percentage = calculate_overlap(bbox, prev_bbox)
    if overlap_percentage > overlap_threshold:
        print("Object overlap with background detected")
        break

    # Update previous bounding box
    prev_bbox = bbox

# Release video capture
cap.release()
cv2.destroyAllWindows()
