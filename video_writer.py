import os
from multiprocessing import Queue
from queue import Empty
from threading import Thread
import time
import cv2


class AsyncVideoWriter:
    """Video Writer"""

    def __init__(self, config):
        self.config = config
        self.fourcc = cv2.VideoWriter_fourcc(*self.config.store_codec)
        self.video_out = None
        self.stop_time = None
        self.stopped = True
        self.activity_count = 0
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
            print("AsyncVideoWriter start {:.2f} s".format(time.perf_counter()))
            return True
        return False

    def stop(self, activity_count):
        if not self.stopped:
            self.stop_time = time.perf_counter()
            self.stopped = True
            self.activity_count = activity_count
            # never block the main processing loop
            # if self.writer_thread is not None:
            #    self.writer_thread.join()
            print("AsyncVideoWriter stop {:.2f} s, activity: {}".format(self.stop_time, activity_count))

    def write(self, frame):
        if not self.stopped:
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            else:
                print("[WARNING] Writer queue is full, system will clean up the whole queue. It will result in frame "
                      "drops.")
                try:
                    while True:
                        self.frame_queue.get_nowait()
                except Empty:
                    pass
                #self.frame_queue.clear()

    def _writer_thread(self):
        video_out = cv2.VideoWriter(self.filename, self.fourcc, self.config.frame_rate,
                                    (self.config.resolution[0], self.config.resolution[1]))
        empty = False
        while not self.stopped or not empty:
            try:
                frame = self.frame_queue.get(block=True, timeout=1)
            except Empty:
                # print("Queue empty")
                empty = True
                continue
            video_out.write(frame)

        finished_time = time.perf_counter()
        print("AsyncVideoWriter encoding and writing finished {:.2f} s, time lag {:.2f} s"
              .format(finished_time, finished_time-self.stop_time))
        video_out.release()
        if self.activity_count < self.config.store_activity_count_threshold:
            print("AsyncVideoWriter remove recording due to less activity {}".format(self.activity_count))
            os.remove(self.filename)
        self.is_writing = False
