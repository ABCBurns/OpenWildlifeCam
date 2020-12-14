import time

from picamera.array import PiRGBArray
from picamera import PiCamera


class CapturePiCamera:
    """Capture frame with Opencv"""

    def __init__(self, config):
        self.camera = PiCamera()
        self.camera.resolution = config.resolution
        self.camera.framerate = config.frame_rate
        self.raw_capture = PiRGBArray(self.camera, size=config.resolution)
        print("camera model: " + self.camera.revision)
        print("frame rate: " + str(self.camera.framerate))
        # camera to warmup
        time.sleep(0.1)

    def start(self):
        return self

    def stop(self):
        self.raw_capture.close()
        self.camera.close()

    def capture_frame(self):
        self.camera.capture(self.raw_capture, format="bgr", use_video_port=True)
        # grab the raw numpy array
        frame = self.raw_capture.array
        self.raw_capture.truncate(0)
        return frame
