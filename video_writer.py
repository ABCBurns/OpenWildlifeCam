from queue import Queue
from queue import Empty
from threading import Thread
import time

import cv2


class AsyncVideoWriter:
    """Video Writer"""

    def __init__(self, config):
        self.config = config
        self.fourcc = cv2.VideoWriter_fourcc(*'x264')
        self.video_out = None
        self.stop_time = None
        self.stopped = True
        self.is_writing = False
        self.filename = None
        self.frame_queue = Queue(128)
        self.writer_thread = None

    def start(self, filename):
        if not self.is_writing:
            self.stopped = False
            self.is_writing = True
            self.filename = filename
            self.writer_thread = Thread(target=self._writer_thread, args=())
            self.writer_thread.start()
            print("AsyncVideoWriter start {} seconds".format(time.perf_counter()))
            return True
        return False

    def stop(self):
        if not self.stopped:
            self.stop_time = time.perf_counter()
            self.stopped = True
            # never block the main processing loop
            # if self.writer_thread is not None:
            #    self.writer_thread.join()
            print("AsyncVideoWriter stop {} seconds".format(self.stop_time))

    def write(self, frame):
        if not self.stopped:
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                print("writer queue is full")

    def _writer_thread(self):
        video_out = cv2.VideoWriter(self.filename, self.fourcc, self.config.frame_rate,
                                    (self.config.resolution[0], self.config.resolution[1]))
        empty = False
        while not self.stopped or not empty:
            try:
                frame = self.frame_queue.get(block=True, timeout=1)
            except Empty:
                print("Queue empty")
                empty = True
                continue
            video_out.write(frame)

        finished_time = time.perf_counter()
        print("AsyncVideoWriter stop, finished {} lag {} seconds"
              .format(finished_time, finished_time-self.stop_time))
        video_out.release()
        is_writing = False
