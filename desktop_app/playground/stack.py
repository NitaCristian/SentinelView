# 3
#
# I
# have
# the
# following
# code
# where
# the
# user
# can
# press
# p
# to
# pause
# the
# video, draw
# a
# bounding
# box
# around
# the
# object
# to
# be
# tracked, and then
# press
# Enter(carriage
# return) to
# track
# that
# object in the
# video
# feed:
#
# import cv2
# import sys
#
# major_ver, minor_ver, subminor_ver = cv2.__version__.split('.')
#
# if __name__ == '__main__':
# # Set up tracker.
#     tracker_types = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']
# tracker_type = tracker_types[1]
#
# if int(minor_ver) < 3:
#     tracker = cv2.Tracker_create(tracker_type)
# else:
#     if
# tracker_type == 'BOOSTING':
# tracker = cv2.TrackerBoosting_create()
# if tracker_type == 'MIL':
#     tracker = cv2.TrackerMIL_create()
# if tracker_type == 'KCF':
#     tracker = cv2.TrackerKCF_create()
# if tracker_type == 'TLD':
#     tracker = cv2.TrackerTLD_create()
# if tracker_type == 'MEDIANFLOW':
#     tracker = cv2.TrackerMedianFlow_create()
# if tracker_type == 'GOTURN':
#     tracker = cv2.TrackerGOTURN_create()
# if tracker_type == 'MOSSE':
#     tracker = cv2.TrackerMOSSE_create()
# if tracker_type == "CSRT":
#     tracker = cv2.TrackerCSRT_create()
#
# # Read video
# video = cv2.VideoCapture(
#     0)  # 0 means webcam. Otherwise if you want to use a video file, replace 0 with "video_file.MOV")
#
# # Exit if video not opened.
# if not video.isOpened():
#     print("Could not open video")
# sys.exit()
#
# while True:
#
#     # Read first frame.
#     ok, frame = video.read()
#     if not ok:
#         print('Cannot read video file')
#         sys.exit()
#
#     # Retrieve an image and Display it.
#     if ((0xFF & cv2.waitKey(10)) == ord('p')):  # Press key `p` to pause the video to start tracking
#         break
#     cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
#     cv2.imshow("Image", frame)
# cv2.destroyWindow("Image");
#
# # select the bounding box
# bbox = (287, 23, 86, 320)
#
# # Uncomment the line below to select a different bounding box
# bbox = cv2.selectROI(frame, False)
#
# # Initialize tracker with first frame and bounding box
# ok = tracker.init(frame, bbox)
#
# while True:
#     # Read a new frame
#     ok, frame = video.read()
#     if not ok:
#         break
#
#     # Start timer
#     timer = cv2.getTickCount()
#
#     # Update tracker
#     ok, bbox = tracker.update(frame)
#
#     # Calculate Frames per second (FPS)
#     fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer);
#
#     # Draw bounding box
#     if ok:
#         # Tracking success
#         p1 = (int(bbox[0]), int(bbox[1]))
#         p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
#         cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
#     else:
#         # Tracking failure
#         cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
#
#     # Display tracker type on frame
#     cv2.putText(frame, tracker_type + " Tracker", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
#
#     # Display FPS on frame
#     cv2.putText(frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
#
#     # Display result
#     cv2.imshow("Tracking", frame)
#
#     # Exit if ESC pressed
#     k = cv2.waitKey(1) & 0xff
#     if k == 27: break
#
# Now, instead
# of
# having
# the
# user
# pause
# the
# video and draw
# the
# bounding
# box
# around
# the
# object, how
# do
# I
# make
# it
# such
# that
# it
# can
# automatically
# detect
# the
# particular
# object
# I
# am
# interested in (which is toothbrush in my case)
# whenever
# it is introduced in the
# video
# feed, and then
# track
# it?
#
# I
# found
# this
# article
# which
# talks
# about
# how
# we
# can
# detect
# objects in video
# using
# ImageAI and Yolo.
#
# from imageai.Detection import VideoObjectDetection
# import os
# import cv2
#
# execution_path = os.getcwd()
#
# camera = cv2.VideoCapture(0)
#
# detector = VideoObjectDetection()
# detector.setModelTypeAsYOLOv3()
# detector.setModelPath(os.path.join(execution_path, "yolo.h5"))
# detector.loadModel()
#
# video_path = detector.detectObjectsFromVideo(camera_input=camera,
#                                              output_file_path=os.path.join(execution_path, "camera_detected_1")
#                                              , frames_per_second=29, log_progress=True)
# print(video_path)
#
# Now, Yolo
# does
# detect
# toothbrush, it is among
# the
# 80
# odd
# objects
# that
# it
# can
# detect
# by
# default.However, there
# are
# 2
# points
# about
# this
# article
# that
# makes
# it
# not the
# ideal
# solution
# for me:
#
#     This
#     method
#     first
#     analyses
#     each
#     video
#     frame(takes
#     about
#     1 - 2
#     seconds
#     per
#     frame, so
#     about
#     1
#     minute
#     to
#     analyse
#     a
#     2 - 3
#     second
#     video
#     stream
#     from the webcam), and saves
#     the
#     detected
#     video in a
#     separate
#     video
#     file.Whereas, I
#     want
#     to
#     detect
#     the
#     toothbrush in the
#     webcam
#     video
#     feed in real
#     time.Is
#     there
#     a
#     solution
#     for this?
#
#     The
#     Yolo
#     v3
#     model
#     being
#     used
#     can
#     detect
#     all
#     80
#     objects, but
#     I
#     want
#     only
#     2 or 3
#     objects
#     detected - the
#     toothbrush, the
#     person
#     holding
#     the
#     toothbrush and the
#     background
#     possibly,
#     if needed at all.So, is there a way in which I can reduce the model weight by selecting only these 2 or 3 objects to detect?
#
#     python - 3.
#     xopencvdeep - learningobject - detectionvideo - tracking
#
# Share
# Improve
# this
# question
# Follow
# asked
# Feb
# 8, 2021
# at
# 5: 14
# Kristada673
# 's user avatar
# Kristada673
# 3, 65077
# gold
# badges4545
# silver
# badges9898
# bronze
# badges
#
# You
# dont
# use
# darknet
# framework ? –
# Yunus
# Temurlenk
# Feb
# 8, 2021
# at
# 5: 38
# I
# have
# no
# idea
# about
# it.I
# don
# 't have much experience in the field of Computer Vision, I'
# m
# just
# trying
# to
# get
# into
# it.So,
# if you think darknet can help solve this problem, I'd appreciate it greatly if you could please write an answer about how. –
# Kristada673
# Feb
# 8, 2021
# at
# 5: 43
#
# Add
# a
# comment
# 2
# Answers
# Sorted
# by:
# 1
#
# If
# you
# want
# a
# quick and easy
# solution, you
# can
# use
# one
# of
# the
# more
# lightweight
# yolo
# files.You
# can
# get
# the
# weights and config
# files(they
# come in pairs and must
# be
# used
# together) from this website: https: // pjreddie.com / darknet / yolo / (don't worry, it looks sketch but it's fine)
#
# Using
# a
# smaller
# network
# will
# get
# you
# much
# higher
# fps, but
# also
# worse
# accuracy.If
# that
# 's a tradeoff you'
# re
# willing
# to
# accept
# then
# this is the
# easiest
# thing
# to
# do.
#
# Here
# 's some code for detecting toothbrushes. The first file is just a class file to help make using the Yolo network more seamless. The second is the "main" file that opens up a VideoCapture and feeds images to the network.
#
# yolo.py
#
# import cv2
# import numpy as np
#
#
# class Yolo:
#     def __init__(self, cfg, weights, names, conf_thresh, nms_thresh, use_cuda=False):
#         # save thresholds
#         self.ct = conf_thresh;
#         self.nmst = nms_thresh;
#
#         # create net
#         self.net = cv2.dnn.readNet(weights, cfg);
#         print("Finished: " + str(weights));
#         self.classes = [];
#         file = open(names, 'r');
#         for line in file:
#             self.classes.append(line.strip());
#
#         # use gpu + CUDA to speed up detections
#         if use_cuda:
#             self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA);
#             self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA);
#
#         # get output names
#         layer_names = self.net.getLayerNames();
#         self.output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()];
#
#     # runs detection on the image and draws on it
#     def detect(self, img, target_id):
#         # get detection stuff
#         b, c, ids, idxs = self.get_detection_data(img, target_id);
#
#         # draw result
#         img = self.draw(img, b, c, ids, idxs);
#         return img, len(idxs);
#
#     # returns boxes, confidences, class_ids, and indexes (indices?)
#     def get_detection_data(self, img, target_id):
#         # get output
#         layer_outputs = self.get_inf(img);
#
#         # get dims
#         height, width = img.shape[:2];
#
#         # filter thresholds and target
#         b, c, ids, idxs = self.thresh(layer_outputs, width, height, target_id);
#         return b, c, ids, idxs;
#
#     # runs the network on an image
#     def get_inf(self, img):
#         # construct a blob
#         blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False);
#
#         # get response
#         self.net.setInput(blob);
#         layer_outputs = self.net.forward(self.output_layers);
#         return layer_outputs;
#
#     # filters the layer output by conf, nms and id
#     def thresh(self, layer_outputs, width, height, target_id):
#         # some lists
#         boxes = [];
#         confidences = [];
#         class_ids = [];
#
#         # each layer outputs
#         for output in layer_outputs:
#             for detection in output:
#                 # get id and confidence
#                 scores = detection[5:];
#                 class_id = np.argmax(scores);
#                 confidence = scores[class_id];
#
#                 # filter out low confidence
#                 if confidence > self.ct and class_id == target_id:
#                     # scale bounding box back to the image size
#                     box = detection[0:4] * np.array([width, height, width, height]);
#                     (cx, cy, w, h) = box.astype('int');
#
#                     # grab the top-left corner of the box
#                     tx = int(cx - (w / 2));
#                     ty = int(cy - (h / 2));
#
#                     # update lists
#                     boxes.append([tx, ty, int(w), int(h)]);
#                     confidences.append(float(confidence));
#                     class_ids.append(class_id);
#
#         # apply NMS
#         idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.ct, self.nmst);
#         return boxes, confidences, class_ids, idxs;
#
#     # draw detections on image
#     def draw(self, img, boxes, confidences, class_ids, idxs):
#         # check for zero
#         if len(idxs) > 0:
#             # loop over indices
#             for i in idxs.flatten():
#                 # extract the bounding box coords
#                 (x, y) = (boxes[i][0], boxes[i][1]);
#                 (w, h) = (boxes[i][2], boxes[i][3]);
#
#                 # draw a box
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2);
#
#                 # draw text
#                 text = "{}: {:.4}".format(self.classes[class_ids[i]], confidences[i]);
#                 cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2);
#         return img;
#
#
#
# import cv2
# import numpy as np
#
# # this is the "yolo.py" file, I assume it's in the same folder as this program
# from yolo import Yolo
#
# # these are the filepaths of the yolo files
# weights = "yolov3-tiny.weights";
# config = "yolov3-tiny.cfg";
# labels = "yolov3.txt";
#
# # init yolo network
# target_class_id = 79; # toothbrush
# conf_thresh = 0.4; # less == more boxes (but more false positives)
# nms_thresh = 0.4; # less == more boxes (but more overlap)
# net = Yolo(config, weights, labels, conf_thresh, nms_thresh);
#
# # open video capture
# cap = cv2.VideoCapture(0);
#
# # loop
# done = False;
# while not done:
#     # get frame
#     ret, frame = cap.read();
#     if not ret:
#         done = cv2.waitKey(1) == ord('q');
#         continue;
#
#     # do detection
#     frame, _ = net.detect(frame, target_class_id);
#
#     # show
#     cv2.imshow("Marked", frame);
#     done = cv2.waitKey(1) == ord('q');
