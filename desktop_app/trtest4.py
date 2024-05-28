import cv2

# Initialize video capture
cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')

# Skip the first 100 frames
for _ in range(200):
    ret, _ = cap.read()
    if not ret:
        break

# Initialize the video frame
ret, frame = cap.read()
if not ret:
    exit()

# Select ROI
bbox = cv2.selectROI('Select ROI', frame, fromCenter=False, showCrosshair=True)
cv2.destroyWindow('Select ROI')

# Initialize the CSRT tracker
tracker = cv2.legacy.TrackerKCF_create()
tracker.init(frame, bbox)

# Process each frame
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Update the tracker
    success, bbox = tracker.update(frame)

    if success:
        # Draw bounding box on the frame
        x, y, w, h = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Tracking', frame)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
