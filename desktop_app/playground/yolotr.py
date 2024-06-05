from ultralytics import YOLO

model = YOLO('../yolov8n.pt')

results = model.track(source='../detections/20240605_181853.avi', show=True)
