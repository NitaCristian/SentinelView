import cv2
import numpy as np

# Initialize video capture
cap = cv2.VideoCapture('files/Traffic_Laramie_1.mp4')

# Parameters for ViBe algorithm
num_samples = 20  # Number of samples per pixel
min_match = 2     # Minimum matches to consider pixel as background
radius = 20       # Radius for selecting random samples
subsample_factor = 16  # Subsampling factor for speed-up

# Initialize ViBe model
def initialize_vibe_model(frame):
    model = np.zeros((frame.shape[0], frame.shape[1], num_samples), dtype=np.uint8)
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            for k in range(num_samples):
                row = np.random.randint(max(0, i - radius), min(frame.shape[0], i + radius))
                col = np.random.randint(max(0, j - radius), min(frame.shape[1], j + radius))
                model[i, j, k] = frame[row, col]
    return model

# Apply ViBe background subtraction
def vibe_background_subtraction(frame, model):
    fg_mask = np.zeros_like(frame, dtype=np.uint8)
    for i in range(frame.shape[0]):
        for j in range(frame.shape[1]):
            count = 0
            for k in range(num_samples):
                if np.abs(frame[i, j] - model[i, j, k]) < 20:
                    count += 1
                    if count >= min_match:
                        break
            if count >= min_match:
                fg_mask[i, j] = 0
            else:
                fg_mask[i, j] = 255
                if np.random.randint(subsample_factor) == 0:
                    index = np.random.randint(num_samples)
                    model[i, j, index] = frame[i, j]
    return fg_mask

# Process each frame with ViBe
ret, frame = cap.read()
if ret:
    model = initialize_vibe_model(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply ViBe background subtraction
    fg_mask = vibe_background_subtraction(gray_frame, model)

    # Display the foreground mask
    cv2.imshow('Foreground Mask', fg_mask)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Release video capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
