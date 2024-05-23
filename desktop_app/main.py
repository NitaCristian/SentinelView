import sys

import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        self.start_button = None
        self.camera_label = None
        self.layout = None
        self.stop_button = None
        self.init_ui()

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def init_ui(self):
        self.setWindowTitle("Camera Surveillance System")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label)

        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_camera)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera", self)
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

    def start_camera(self):
        self.timer.start(20)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_camera(self):
        self.timer.stop()
        self.capture.release()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.camera_label.clear()

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
