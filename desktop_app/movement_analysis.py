import math
import os
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
    if not os.path.exists('special'):
        os.makedirs('special')

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    basename = os.path.basename(video_path)
    annotated_video_path = os.path.join('special', f'{os.path.splitext(basename)[0]}_annotated.avi')
    summary_path = os.path.join('special', f'{os.path.splitext(basename)[0]}_summary.txt')

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(annotated_video_path, fourcc, fps, (width, height))

    summary_lines = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects in the frame
        results = model(frame, stream=True)

        # Filter detections for persons
        detections = []
        for result in results:
            for box in result.boxes:
                conf = math.ceil(box.conf[0] * 100) / 100
                if conf < conf_threshold:
                    continue

                cls_id = int(box.cls[0])
                curr_class = classes[cls_id]

                if curr_class == 'person':
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
            # TODO: Fix drawing boxes in the right position
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            # Record summary
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # in seconds
            # TODO: Only append this at the start of the tracking
            summary_lines.append(f'Person detected at {timestamp:.2f} seconds, Track ID: {track_id}')

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

    # Initialize YOLOv8 model
    model = YOLO('yolov8n.pt')  # You can use a smaller version like yolov8s.pt for speed

    # Initialize DeepSORT tracker
    tracker = DeepSort(max_age=30, n_init=3, nn_budget=70)

    conf_threshold = 0.63

    with open("./models/coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    detections_folder = 'detections'
    video_files = [os.path.join(detections_folder, f) for f in os.listdir(detections_folder) if f.endswith('.avi')]

    for video_file in video_files:
        process_video(video_file)
