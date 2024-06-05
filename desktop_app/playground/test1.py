import math

import cv2 as cv


def is_collision(rect1, rect2):
    """
    Checks if two bounding boxes collide.

    :param rect1: Coordinates of the first bounding box (x, y, width, height)
    :param rect2: Coordinates of the second bounding box (x, y, width, height)
    :return: True if the bounding boxes collide, False otherwise
    """
    # Extract dimensions of the first bounding box
    x1, y1, w1, h1 = rect1
    # Compute centroid of the first bounding box
    cx1 = x1 + w1 // 2
    cy1 = y1 + h1 // 2

    # Extract dimensions of the second bounding box
    x2, y2, w2, h2 = rect2
    # Compute centroid of the second bounding box
    cx2 = x2 + w2 // 2
    cy2 = y2 + h2 // 2

    # Return whether the distance between the centroids is less than 50
    return math.hypot(cx1 - cx2, cy1 - cy2) < 50


def get_bounding_boxes(image):
    """
    Detects bounding boxes present in a given frame from video capture.

    :param image: A frame from the video capture.
    :return: List of bounding boxes present in the image.
    """
    boxes = []
    contours, _ = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # Ignore small areas (likely noise or small objects)
        if cv.contourArea(contour) < 4000:
            continue
        box = cv.boundingRect(contour)
        # Ignore boxes positioned above the main street
        if box[1] < 300:
            continue
        boxes.append(box)
    return boxes


def display_bounding_boxes(image, boxes, color=(0, 255, 0)):
    """
    Displays a rectangle for each bounding box in the given image.

    :param image: Frame from the video capture.
    :param boxes: List of bounding boxes.
    :param color: Color of the rectangle. Defaults to green.
    """
    # Iterate over each bounding box
    for box in boxes:
        (x, y, w, h) = box
        cv.rectangle(image, (x, y), (x + w, y + h), color, 1)


def display_active_area(frame):
    """
    Displays a line and text indicating the main street on the given frame.

    :param frame: Frame from the video capture.
    """
    cv.putText(frame, 'Main Street', (0, 280), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
    cv.line(frame, (0, 300), (1050, 300), (0, 0, 255), 2)


def display_data(frame, frame_number, to_left):
    """
    Displays tracking information such as the current frame number and the number of cars tracked towards the city's center.

    :param frame: Frame from the video capture.
    :param frame_number: The current frame number.
    :param to_left: List of cars tracked towards the city's center.
    """
    cv.putText(frame, f'Frame: {frame_number}', (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2, cv.LINE_AA)
    cv.putText(frame, f'Cars to city\'s center: {len(to_left)}', (0, 100), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2,
               cv.LINE_AA)


def eliminate_inactive_objects(tracking_objects, updated):
    """
    Eliminates inactive objects from the tracking list.

    :param tracking_objects: List of tracked objects.
    :param updated: Set of updated object IDs.
    """
    # Create a copy of the tracking dictionary to avoid modifying it while iterating
    _c = tracking_objects.copy()
    # Iterate over each tracked object
    for object_id, box in _c.items():
        # If the object ID is not in the set of updated objects, it means the object is inactive
        if object_id not in updated:
            # Remove the inactive object from the tracking dictionary
            tracking_objects.pop(object_id)


def update_objects(current_bounding_boxes, tracking_objects, updated, tracking_id, to_left):
    """
    Updates the bounding boxes of currently tracked cars. If they are new objects, adds them to the list.

    :param current_bounding_boxes: Bounding boxes from the current frame.
    :param tracking_objects: Dictionary of tracked cars {object_id: bounding_box}.
    :param updated: List containing the IDs of the updated car objects.
    :param tracking_id: Current ID of the tracked object.
    :param to_left: Set of object IDs of cars moving towards the city's center.
    :return: Updated tracking_id after adding new cars.
    """
    # Iterate over each bounding box in the current frame
    for bounding_box in current_bounding_boxes:
        is_similar = False
        # Check if the current bounding box matches with any existing tracked object
        for object_id, box in tracking_objects.items():
            if is_collision(bounding_box, box):
                # If there is a match, update the bounding box of the tracked object
                tracking_objects[object_id] = bounding_box
                # Add the object ID to the list of updated objects
                updated.append(object_id)
                # If the x position of the current bounding box is less than the bounding box of the tracked car,
                # it means that it is moving to the left, so store it in the set
                if bounding_box[0] < box[0] - 5:
                    to_left.add(object_id)
                is_similar = True
                break
        # If the bounding box doesn't match with any existing object, consider it as a new object
        if not is_similar:
            # Increment the tracking ID for the new object
            tracking_id += 1
            # Add the new object ID to the list of updated objects
            updated.append(tracking_id)
            # Add the new object to the tracking dictionary with its bounding box
            tracking_objects[tracking_id] = bounding_box
    return tracking_id


# Open video capture
cap = cv.VideoCapture('files/Traffic_Laramie_1.mp4')
if not cap.isOpened():
    print('Error opening video stream or file')
    exit()

# Dictionary to store tracking objects
tracking_objects = {}
# Counter to track object IDs
tracking_id = 0
# Counter to track frame number
frame_number = 0
# Placeholder for the first frame
first_frame = None
# Set of car ID that move to the city's center
to_left = set()

# Main loop to process each frame of the video
while True:
    # Read frame from video capture
    ret, frame = cap.read()
    if not ret:
        print('Error reading video file or reached the end of the video')
        break

    # Convert frame to grayscale
    mask = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    if first_frame is None:
        # Save the first frame for later subtraction
        first_frame = mask
        continue

    # Background subtraction
    mask = cv.absdiff(mask, first_frame)
    mask = cv.GaussianBlur(mask, (45, 45), 0)
    mask = cv.threshold(mask, 25, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]

    # Get bounding boxes of objects in the frame
    current_bounding_boxes = get_bounding_boxes(mask)

    # Update tracking objects and eliminate inactive ones
    updated = []
    tracking_id = update_objects(current_bounding_boxes, tracking_objects, updated, tracking_id, to_left)
    eliminate_inactive_objects(tracking_objects, updated)

    # Display bounding boxes and additional data on the frame
    display_bounding_boxes(frame, tracking_objects.values())
    display_data(frame, frame_number, to_left)
    display_active_area(frame)

    # Increment frame counter
    frame_number += 1

    # Display frame
    cv.imshow('frame', frame)
    # Exit condition
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture
cap.release()
# Close OpenCV windows
cv.destroyAllWindows()

# Print statistics
print(f'Total number of cars moving to city\'s center: {len(to_left)}')
print(f'Total number of frames: {frame_number}')

seconds = frame_number / 25
print(f'Total number of seconds: {seconds}')
minutes = round(seconds / 60)
print(f'Total number of minutes: {minutes}')

cars_per_minute = 0
if minutes != 0:
    cars_per_minute = round(len(to_left) / minutes)
print(f'Total number of moving to city\'s center per minute: {cars_per_minute}')
