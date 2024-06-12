import math
import os
import sys
import cv2
import requests
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

API_URL = "http://127.0.0.1:5001/api"


def upload_to_api(video_path, summary_path):
    """
    Uploads the annotated video and summary to the API.

    Parameters:
    video_path (str): Path to the annotated video file.
    summary_path (str): Path to the summary text file.
    """
    try:
        # Read the summary file content
        with open(summary_path, 'r') as summary_file:
            summary_content = summary_file.read()

        # Prepare the data payload
        data = {
            'file_path': os.path.basename(video_path),
            'duration': get_video_duration(video_path)
        }

        headers = {
            'Content-Type': 'application/json'
        }

        proxies = {'https': 'http://127.0.0.1:5001'}
        # Send the POST request to the API
        response = requests.post(f'{API_URL}/insert_footage', headers=headers, json=data, verify=False, proxies=proxies)

        if response.status_code == 200:
            print("Files uploaded successfully.")
            footage_id = response.json().get('id')

            # Insert an event associated with this footage
            insert_event(footage_id, summary_content)

        else:
            print(f"Failed to upload files. Status code: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(f"An error occurred while uploading files: {e}")


def insert_event(footage_id, summary):
    """
    Inserts an event related to the uploaded footage.

    Parameters:
    footage_id (int): The ID of the uploaded footage.
    summary (str): Summary details to include in the event title.
    """
    try:
        event_data = {
            'event_type': 'Person Detected',
            'title': f'Footage ID {footage_id}',
            'footage_id': footage_id
        }

        headers = {
            'Content-Type': 'application/json'
        }

        proxies = {'https': 'http://127.0.0.1:5001'}
        # Send the POST request to insert the event
        response = requests.post(f"{API_URL}/insert_event", headers=headers, json=event_data, verify=False,
                                 proxies=proxies)

        if response.status_code == 200:
            print("Event inserted successfully.")
        else:
            print(f"Failed to insert event. Status code: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print(f"An error occurred while inserting event: {e}")


def get_video_duration(video_path):
    """
    Get the duration of the video in seconds.

    Parameters:
    video_path (str): Path to the video file.

    Returns:
    float: Duration of the video in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    cap.release()
    return duration


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

    # Upload the annotated video and summary to the API
    upload_to_api(annotated_video_path, summary_path)


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
