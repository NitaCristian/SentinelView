import sys

import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class CameraApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.show_subtraction = False

    def init_ui(self):
        self.setWindowTitle("Camera Surveillance System")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.camera_label = QLabel(self)
        self.layout.addWidget(self.camera_label)

        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Camera", self)
        self.start_button.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera", self)
        self.stop_button.clicked.connect(self.stop_camera)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        self.toggle_button = QPushButton("Enable Background Subtraction", self)
        self.toggle_button.clicked.connect(self.toggle_subtraction)
        button_layout.addWidget(self.toggle_button)

        self.layout.addLayout(button_layout)
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

    def toggle_subtraction(self):
        self.show_subtraction = not self.show_subtraction
        if self.show_subtraction:
            self.toggle_button.setText("Disable Background Subtraction")
        else:
            self.toggle_button.setText("Enable Background Subtraction")

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            if self.show_subtraction:
                fg_mask = self.bg_subtractor.apply(frame)
                frame = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2RGB)
            else:
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
