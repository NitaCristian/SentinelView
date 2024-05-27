import cv2
import numpy as np

cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')

frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
frameIds = frame_count * np.random.uniform(size=25)
frameIds = np.arange(min(25, frame_count))

frames = []
for fid in frameIds:
    cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
    ret, frame = cap.read()
    frames.append(frame)

medianFrame = np.median(frames, axis=0).astype(dtype=np.uint8)

cv2.imshow('frame', medianFrame)
cv2.waitKey(0)

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

grayMedianFrame = cv2.cvtColor(medianFrame, cv2.COLOR_BGR2GRAY)

ret = True
while ret:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    dframe = cv2.absdiff(frame, grayMedianFrame)
    th, dframe = cv2.threshold(dframe, 30, 255, cv2.THRESH_BINARY)
    cv2.imshow('frame', dframe)
    cv2.waitKey(20)

cap.release()
cv2.destroyAllWindows()
