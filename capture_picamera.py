import time
from multiprocessing import Queue
from threading import Thread

from picamera.array import PiRGBArray
from picamera import PiCamera


class CapturePiCameraSync:
    """Capture frame with PiCamera synchronously"""

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

    def read(self):
        self.camera.capture(self.raw_capture, format="bgr", use_video_port=True)
        # grab the raw numpy array
        frame = self.raw_capture.array
        self.raw_capture.truncate(0)
        return frame


class CapturePiCameraAsync:
    """Capture frame with PiCamera asynchronously (in own thread)"""

    def __init__(self, config):
        self.camera = PiCamera()
        self.camera.resolution = config.resolution
        self.camera.framerate = config.frame_rate
        self.raw_capture = PiRGBArray(self.camera, size=config.resolution)
        self.stream = self.camera.capture_continuous(self.raw_capture,
                                                     format="bgr", use_video_port=True)
        print("camera model: " + self.camera.revision)
        print("frame rate: " + str(self.camera.framerate))
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
        for f in self.stream:
            if self.stopped:
                break
            frame = f.array
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                print("[WARNING] Capture queue is full, system cleans up whole queue. It will result in frame drops.")
                self._clean_queue
            self.raw_capture.truncate(0)

    def _clean_queue(self):
        try:
            while True:
                self.frame_queue.get_nowait()
        except Empty:
            pass
