import math
import os
import sys

import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort


def process_video(video_path):
    """
    Process the video for person detection and tracking, and save annotated video and summary.

    Parameters:
    video_path (str): Path to the input video file.
    """
    # Create directories if they don't exist
    if not os.path.exists('analyses'):
        os.makedirs('analyses')

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    basename = os.path.basename(video_path)
    annotated_video_path = os.path.join('analyses', f'{os.path.splitext(basename)[0]}_annotated.avi')
    summary_path = os.path.join('analyses', f'{os.path.splitext(basename)[0]}_summary.txt')

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(annotated_video_path, fourcc, fps, (width, height))

    summary_lines = []
    logged_tracks = set()  # Set to keep track of logged person IDs

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects in the frame
        results = model(frame, stream=True, verbose=False)

        # Filter detections for persons
        detections = []
        for result in results:
            for box in result.boxes:
                conf = math.ceil(box.conf[0] * 100) / 100
                if conf < 0.63:
                    continue

                cls_id = int(box.cls[0])
                curr_class = classes[cls_id]

                if curr_class in ['person', 'dog', 'cat']:
                    x, y, w, h = map(int, box.xywh[0])
                    detections.append(([x, y, w, h], conf, cls_id))

        # Update tracker
        tracks = tracker.update_tracks(detections, frame=frame)

        # Draw bounding boxes and track ids
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            bbox = track.to_tlbr()
            x1, y1, x2, y2 = map(int, bbox)

            # Drawing bounding box and ID
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            # Record summary if this ID hasn't been logged yet
            if track_id not in logged_tracks:
                timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # in seconds
                summary_lines.append(f'Person detected at {timestamp:.2f} seconds, Track ID: {track_id}')
                logged_tracks.add(track_id)

        # Write the frame to the output video
        out.write(frame)

    # Release resources
    cap.release()
    out.release()

    # Write summary to a text file
    with open(summary_path, 'w') as file:
        for line in summary_lines:
            file.write(line + '\n')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python movement_analysis.py <file_path>")
        sys.exit(1)

    model = YOLO('yolov8n.pt')
    tracker = DeepSort(max_age=30, n_init=3, nn_budget=70)

    with open("./coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    file_path = sys.argv[1]
    print(f"Analyzing video {file_path}")
    process_video(file_path)
    print(f"Done analyzing video {file_path}")
