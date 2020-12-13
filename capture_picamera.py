import time

from picamera.array import PiRGBArray
from picamera import PiCamera


class CapturePicamera:
    """Capture frame with Opencv"""

    def __init__(self, config):
        self.camera = PiCamera()
        self.camera.resolution = config.resolution
        self.camera.framerate = config.frame_rate
        self.rawCapture = PiRGBArray(camera, size=config.resolution)
        print("camera model: " + self.camera.revision)
        print("frame rate: " + str(self.camera.framerate))
        # camera to warmup
        time.sleep(0.1)

    def capture_frame(self):
        capture_frame = self.camera.capture(self.rawCapture, format="bgr", use_video_port=True)
        # grab the raw numpy array
        frame = capture_frame.array
        capture_frame.truncate(0)
        return frame
