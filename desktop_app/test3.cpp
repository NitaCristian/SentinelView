#include <opencv2/opencv.hpp>
#include <iostream>

using namespace cv;
using namespace std;

int main() {
    // Initialize video capture
    VideoCapture cap("files/Traffic_Laramie_1.mp4");
    if (!cap.isOpened()) {
        cerr << "Error opening video file" << endl;
        return -1;
    }

    // Initialize the MOG2 background subtractor with parameters
    Ptr<BackgroundSubtractorMOG2> mog2 = createBackgroundSubtractorMOG2(500, 16, false);

    // Define morphological operations kernels
    Mat kernel = getStructuringElement(MORPH_ELLIPSE, Size(5, 5));
    Mat small_kernel = getStructuringElement(MORPH_ELLIPSE, Size(3, 3));

    // Set minimum object size threshold
    int min_object_area = 1000;

    // Process each frame with MOG2
    while (true) {
        Mat frame;
        cap >> frame;
        if (frame.empty()) {
            break;
        }

        // Resize frame for faster processing
        resize(frame, frame, Size(640, 360));

        // Apply MOG2 background subtractor to get the foreground mask
        Mat fg_mask;
        mog2->apply(frame, fg_mask);

        // Apply morphological operations to reduce noise
        morphologyEx(fg_mask, fg_mask, MORPH_OPEN, kernel);
        morphologyEx(fg_mask, fg_mask, MORPH_CLOSE, kernel);

        // Apply erosion to remove small noise regions
        erode(fg_mask, fg_mask, small_kernel, Point(-1, -1), 1);

        // Apply a threshold to remove gray pixels (weak foreground regions)
        threshold(fg_mask, fg_mask, 200, 255, THRESH_BINARY);

        // Find contours in the foreground mask
        vector<vector<Point>> contours;
        findContours(fg_mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);

        // Filter contours based on minimum object area
        for (const auto& contour : contours) {
            if (contourArea(contour) < min_object_area) {
                continue;
            }

            // Get bounding box coordinates
            Rect bounding_box = boundingRect(contour);

            // Draw bounding box on the original frame
            rectangle(frame, bounding_box, Scalar(0, 255, 0), 2);
        }

        // Display the frame with bounding boxes
        imshow("Detected Objects", frame);

        if (waitKey(20) == 'q') {
            break;
        }
    }

    // Release video capture and destroy all windows
    cap.release();
    destroyAllWindows();

    return 0;
}
