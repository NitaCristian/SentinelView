import datetime
import math

from ultralytics import YOLO
import cv2


def create_video_writer(video_cap, output_filename):
    # grab the width, height, and fps of the frames in the video stream.
    frame_width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video_cap.get(cv2.CAP_PROP_FPS))

    # initialize the FourCC and a video writer object
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    writer = cv2.VideoWriter(output_filename, fourcc, fps,
                             (frame_width, frame_height))

    return writer


# define some constants
CONFIDENCE_THRESHOLD = 0.8
GREEN = (0, 255, 0)

# initialize the video capture object
video_cap = cv2.VideoCapture("videos/Traffic_Laramie_1.mp4")
# initialize the video writer object
writer = create_video_writer(video_cap, "output.mp4")

# load the pre-trained YOLOv8n model
model = YOLO("models/yolov8n.pt")

while True:
    # start time to compute the fps
    start = datetime.datetime.now()

    ret, frame = video_cap.read()

    # if there are no more frames to process, break out of the loop
    if not ret:
        break

    # run the YOLO model on the frame
    detections = model(frame)

    # loop over the detections
    for result in detections:
        for data in result.boxes:
            # extract the confidence (i.e., probability) associated with the detection
            confidence = math.ceil(data.conf[0] * 100) / 100

            # filter out weak detections by ensuring the
            # confidence is greater than the minimum confidence
            if float(confidence) < CONFIDENCE_THRESHOLD:
                continue

            # if the confidence is greater than the minimum confidence,
            # draw the bounding box on the frame
            x1, y1, x2, y2 = map(int, data.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), GREEN, 2)

    # end time to compute the fps
    end = datetime.datetime.now()
    # show the time it took to process 1 frame
    total = (end - start).total_seconds()
    print(f"Time to process 1 frame: {total * 1000:.0f} milliseconds")

    # calculate the frame per second and draw it on the frame
    fps = f"FPS: {1 / total:.2f}"
    cv2.putText(frame, fps, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    writer.write(frame)
    if cv2.waitKey(1) == ord("q"):
        break

video_cap.release()
writer.release()
cv2.destroyAllWindows()
