import time
from threading import Thread

from picamera.array import PiRGBArray
from picamera import PiCamera


class CapturePiCameraThreaded:
    """Capture frame with Opencv"""

    def __init__(self, config):
        self.camera = PiCamera()
        self.camera.resolution = config.resolution
        self.camera.framerate = config.frame_rate
        self.raw_capture = PiRGBArray(self.camera, size=config.resolution)
        print("camera model: " + self.camera.revision)
        print("frame rate: " + str(self.camera.framerate))
        self.stream = self.camera.capture_continuous(self.raw_capture, format="bgr", use_video_port=True)
        self.frame = None
        self.stopped = False
        time.sleep(0.1)

    def start(self):
        Thread(target=self.capture_thread, args=()).start()
        return self

    def stop(self):
        self.stopped = True

    def capture_frame(self):
        return self.frame

    def capture_thread(self):
        for f in self.stream:
            self.frame = f.array
            self.raw_capture.truncate(0)

            if self.stopped:
                self.stream.close()
                self.raw_capture.close()
                self.camera.close()
                return
