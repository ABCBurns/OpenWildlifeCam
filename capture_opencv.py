from datetime import datetime
import cv2


class CaptureOpencv:
    """Capture frame with Opencv"""

    def __init__(self, config):
        self.config = config
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, config.frame_rate)
        if not self.cap.isOpened():
            print("Cannot open camera")
            exit()

    def start(self):
        return self

    def stop(self):
        self.cap.release()

    def read(self):
        ret, frame = self.cap.read()
        timestamp = datetime.now()
        return frame, timestamp
