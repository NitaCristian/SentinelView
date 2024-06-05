import os

import cv2
import datetime
import time

import numpy as np


def detect_movement(frame, mog2):
    """
    Detects movement in the frame using MOG2 background subtractor and morphological operations.

    Parameters:
    frame (numpy.ndarray): The current video frame.
    mog2 (cv2.BackgroundSubtractorMOG2): The background subtractor object.

    Returns:
    tuple: A boolean indicating if movement is detected, the foreground mask, and the contours.
    """
    fg_mask = mog2.apply(frame)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closing = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return len(contours) > 0, fg_mask, contours


def start_recording(frame, fourcc):
    """
    Starts recording by initializing the VideoWriter object.

    Parameters:
    frame (numpy.ndarray): The current video frame.
    fourcc (cv2.VideoWriter_fourcc): The codec for video recording.

    Returns:
    tuple: The VideoWriter object and the start time of the recording.
    """
    if not os.path.exists('detections'):
        os.makedirs('detections')

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join('detections', f'{timestamp}.avi')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (frame.shape[1], frame.shape[0]))
    return out, time.time()


def calculate_fps(start_time, frame_count):
    """
    Calculates the frames per second (FPS).

    Parameters:
    start_time (float): The start time of the FPS calculation.
    frame_count (int): The number of frames processed.

    Returns:
    float: The calculated FPS.
    """
    elapsed_time = time.time() - start_time
    return frame_count / elapsed_time if elapsed_time > 0 else 0


def non_max_suppression(boxes, overlap_thresh):
    """
    Perform non-max suppression to suppress overlapping bounding boxes.

    Parameters:
    boxes (list): List of bounding boxes.
    overlapThresh (float): Overlap threshold.

    Returns:
    list: List of indices of bounding boxes to keep.
    """
    if len(boxes) == 0:
        return []

    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    pick = []
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = y2

    idxs = idxs.argsort()

    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / area[idxs[:last]]

        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))

    return pick


def main():
    # Initialize video capture object
    cap = cv2.VideoCapture(0)

    # Initialize background subtractor
    mog2 = cv2.createBackgroundSubtractorMOG2(500, 16, True)

    # Define codec for video recording
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Initialize variables
    movement_counter = 0
    recording = False
    recording_start_time = None
    frame_count = 0
    fps_start_time = time.time()
    out = None

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Detect movement in the frame
        detection, fg_mask, contours = detect_movement(frame, mog2)
        if detection:
            movement_counter += 1
        else:
            movement_counter = 0

        # Start recording if movement is detected for more than 1 second
        if movement_counter > 30 and not recording:  # Assuming ~30 FPS, so 30 frames is about 1 second
            out, recording_start_time = start_recording(frame, fourcc)
            recording = True

        if recording:
            out.write(frame)

            # Display recording indicator
            cv2.putText(frame, "Recording", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)

            # Display elapsed recording time
            elapsed_time = time.time() - recording_start_time
            cv2.putText(frame, f'Time: {elapsed_time:.2f}s', (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        cv2.LINE_AA)

            # Stop recording after 20 seconds
            if time.time() - recording_start_time >= 20:
                recording = False
                out.release()

        # Calculate and display FPS
        fps = calculate_fps(fps_start_time, frame_count)
        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Draw bounding boxes around detected movement areas with non-max suppression
        boxes = []
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter out small contours
                x, y, w, h = cv2.boundingRect(contour)
                boxes.append([x, y, x + w, y + h])

        if len(boxes) > 0:
            boxes = np.array(boxes)
            pick = non_max_suppression(boxes, 0.3)
            for i in pick:
                x1, y1, x2, y2 = boxes[i]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow("Feed", frame)

        # Display the foreground mask for debugging purposes
        cv2.imshow("Movement", fg_mask)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
