import time
from queue import Queue
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
        self.frame = None
        self.stopped = False
        self.frame_queue = Queue(128)
        time.sleep(0.1)

    def start(self):
        Thread(target=self._capture_thread, args=()).start()
        return self

    def stop(self):
        self.stopped = True

    def read(self):
        return self.frame_queue.get()

    def _capture_thread(self):
        while not self.stopped:
            if not self.frame_queue.full():
                self.camera.capture(self.raw_capture, format="bgr", use_video_port=True)
                frame = self.raw_capture.array
                self.raw_capture.truncate(0)
                self.frame_queue.put(frame)
            else:
                print("capture queue is full")

