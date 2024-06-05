import numpy as np
import datetime
import cv2
from ultralytics import YOLO

from helper import create_video_writer

conf_threshold = 0.5

# Initialize the video capture and the video writer objects
video_cap = cv2.VideoCapture("1.mp4")
writer = create_video_writer(video_cap, "output.mp4")
# Initialize the YOLOv8 model using the default weights
model = YOLO("yolov8s.pt")

# loop over the frames
while True:
    # starter time to computer the fps
    start = datetime.datetime.now()
    ret, frame = video_cap.read()
    # if there is no frame, we have reached the end of the video
    if not ret:
        print("End of the video file...")
        break
    ############################################################
    ### Detect the objects in the frame using the YOLO model ###
    ############################################################
    # run the YOLO model on the frame
    results = model(frame)
    # loop over the results
    for result in results:
        # initialize the list of bounding boxes, confidences, and class IDs
        bboxes = []
        confidences = []
        class_ids = []
        # loop over the detections
        for data in result.boxes.data.tolist():
            x1, y1, x2, y2, confidence, class_id = data
            x = int(x1)
            y = int(y1)
            w = int(x2) - int(x1)
            h = int(y2) - int(y1)
            class_id = int(class_id)
            # filter out weak predictions by ensuring the confidence is
            # greater than the minimum confidence
            if confidence > conf_threshold:
                bboxes.append([x, y, w, h])
                confidences.append(confidence)
                class_ids.append(class_id)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    ############################################################
    ### Some post-processing to display the results          ###
    ############################################################
    # end time to compute the fps
    end = datetime.datetime.now()
    # calculate the frame per second and draw it on the frame
    fps = f"FPS: {1 / (end - start).total_seconds():.2f}"
    cv2.putText(frame, fps, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 8)
    # show the output frame
    cv2.imshow("Output", frame)
    # write the frame to disk
    writer.write(frame)
    if cv2.waitKey(1) == ord("q"):
        break

# release the video capture, video writer, and close all windows
video_cap.release()
writer.release()
cv2.destroyAllWindows()
