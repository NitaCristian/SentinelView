import cv2
import numpy as np
from sort import Sort  # Import SORT tracker
from ultralytics import YOLO  # Import YOLO model
import math


def non_max_suppression(boxes, scores, iou_threshold):
    indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, iou_threshold)
    return [boxes[i] for i in indices]


def main(video_path, yolo_model_path, conf_threshold=0.5):
    # Load video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    # Initialize background subtractor with optimal parameters for indoor detection
    back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)

    # Initialize SORT tracker
    tracker = Sort()

    # Load YOLO model
    model = YOLO(yolo_model_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Apply background subtraction
        #fg_mask = back_sub.apply(frame)

        # Morphological transformations
        #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        #fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        #fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        #contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #boxes = [cv2.boundingRect(contour) for contour in contours]
        #scores = [1.0] * len(boxes)  # Assuming equal confidence scores

        # Apply non-maximum suppression
        #nms_boxes = non_max_suppression(boxes, scores, 0.3)

        # Update tracker
        #detections = np.array([[x, y, x + w, y + h, s] for (x, y, w, h), s in zip(nms_boxes, scores)])
        #if detections.size == 0:
        #    continue
        #tracked_objects = tracker.update(detections)

        # Perform YOLO detection
        results = model(frame)

        # Process YOLO results
        yolo_boxes = []
        yolo_scores = []
        yolo_labels = []
        for result in results:
            for box in result.boxes:
                conf = math.ceil(box.conf[0] * 100) / 100
                if conf < conf_threshold:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                yolo_boxes.append([x1, y1, x2, y2])
                yolo_scores.append(conf)
                yolo_labels.append(result.names[int(box.cls[0])])

        # Draw bounding boxes and labels
        #for obj in tracked_objects:
        #    x1, y1, x2, y2, obj_id = map(int, obj)
        #    label = 'Object'
        #    for (bx1, by1, bx2, by2), lbl in zip(yolo_boxes, yolo_labels):
        #        if bx1 >= x1 and bx2 <= x2 and by1 >= y1 and by2 <= y2:
        #            label = lbl
        #            break
        #    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
        #    cv2.putText(frame, f'ID {obj_id}: {label}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Display the frame
        cv2.imshow('Frame', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video capture and close windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = "../videos/Traffic_Laramie_1.mp4"
    yolo_model_path = "../models/yolov8n.pt"
    main(video_path, yolo_model_path)
