## Doesn't work

import math
import cv2
from ultralytics import YOLO
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
import numpy as np

# Constants
FILE_PATH = 'files/Traffic_Laramie_1.mp4'
MODEL_PATH = 'yolov8n.pt'
CONFIDENCE_THRESHOLD = 0.63

# Load class names
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Load the YOLO model
model = YOLO(MODEL_PATH)

# Initialize SORT parameters
dt = 1.  # time step
kf = KalmanFilter(dim_x=4, dim_z=2)
kf.F = np.array([[1, dt, 0,  0],    # state transition matrix
                 [0,  1, 0,  0],
                 [0,  0, 1, dt],
                 [0,  0, 0,  1]])
kf.H = np.array([[1, 0, 0, 0],    # measurement function
                 [0, 0, 1, 0]])
kf.R *= 10.   # measurement noise covariance

# Process noise covariance matrix (4x4 for 4-dimensional state space)
# Set the variance according to the dimensionality of the state space
kf.Q = Q_discrete_white_noise(dim=4, dt=dt, var=0.01)

def predict(kf):
    """Predict the next state."""
    kf.predict()


def update(kf, z):
    """Update the Kalman filter with measurement."""
    kf.update(z)


def convert_bbox_to_centroid(bbox):
    """Convert bounding box coordinates to centroid."""
    x1, y1, x2, y2 = bbox
    return [(x1 + x2) / 2, (y1 + y2) / 2]


# Initialize a dictionary to store object ID and track ID correspondence
object_track_ids = {}


def process_frame(frame, model, classes, conf_threshold):
    """Process a single frame, detect objects, and track them using SORT."""
    results = model(frame, stream=True)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            conf = box.conf[0]
            if conf < conf_threshold:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            bbox = [x1, y1, x2, y2]

            cls_id = int(box.cls[0])
            curr_class = classes[cls_id]

            if curr_class == 'car':
                # Predict
                predict(kf)

                # Update measurement
                z = convert_bbox_to_centroid(bbox)
                update(kf, z)

                # Get estimated state
                x, y, _, _ = kf.x

                # Get or assign track ID
                object_id = id(box)
                if object_id not in object_track_ids:
                    object_track_ids[object_id] = len(object_track_ids) + 1
                track_id = object_track_ids[object_id]

                # Draw bounding box and track ID
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f'{curr_class} - ID:{track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 2)
    return frame


# Open the video file
cap = cv2.VideoCapture(FILE_PATH)

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
