import csv
import cv2
import math
import numpy as np
from ultralytics import YOLO
from sort import Sort

# Constants
FILE_PATH = 'files/Traffic_Laramie_1.mp4'
MODEL_PATH = 'yolov8n.pt'
CONFIDENCE_THRESHOLD = 0.63

# Load class names
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize YOLO model
model = YOLO(MODEL_PATH)

# Initialize SORT tracker
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Global variables
roi_selected = False
roi = None

def draw_id(frame, id, pos):
    """Draw track ID on the frame."""
    cv2.putText(frame, str(id), pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def draw_bbox(frame, bbox):
    """Draw bounding box on the frame."""
    x1, y1, x2, y2 = bbox
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)


def process_frame(frame, model, classes, conf_threshold):
    """Process a single frame and draw detections."""
    global roi_selected, roi

    # Perform object detection only within the ROI
    if roi_selected:
        frame = frame[roi[1]:roi[3], roi[0]:roi[2]]

    results = model(frame, stream=True)
    detections = np.empty((0, 5))

    for result in results:
        for box in result.boxes:
            conf = math.ceil(box.conf[0] * 100) / 100
            if conf < conf_threshold:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            if roi_selected:
                x1 += roi[0]
                x2 += roi[0]
                y1 += roi[1]
                y2 += roi[1]
            detections = np.vstack((detections, [x1, y1, x2, y2, conf]))

    # Update tracker with detections
    tracked_objects = tracker.update(detections)

    # Draw tracked objects
    for obj in tracked_objects:
        x1, y1, x2, y2, id = map(int, obj)
        if roi_selected:
            x1 -= roi[0]
            x2 -= roi[0]
            y1 -= roi[1]
            y2 -= roi[1]
        draw_id(frame, id, (max(0, x1), max(35, y1)))
        draw_bbox(frame, (x1, y1, x2, y2))

    return frame


def select_roi(frame):
    """Select a region of interest (ROI) on the first frame."""
    global roi_selected, roi

    roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("Select ROI")
    roi_selected = True
    return roi

# Open the video file
cap = cv2.VideoCapture(FILE_PATH)

# Select ROI on the first frame
ret, first_frame = cap.read()
if ret:
    roi = select_roi(first_frame)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = process_frame(frame, model, classes, CONFIDENCE_THRESHOLD)

    cv2.imshow('YOLO Detection with SORT', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
