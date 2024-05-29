from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model.track(source='files/Traffic_Laramie_1.mp4', show=True, tracker='bytetrack.yaml')