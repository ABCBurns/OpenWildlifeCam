#!/usr/bin/env python

import argparse
import datetime
import os
import shutil
import cv2
from signal import signal, SIGINT

from imutils.video import FPS

from config import WildlifeConfig
from motion import MotionDetection
from notifier import TelegramNotifier
from video_writer import AsyncVideoWriter


def create_video_filename(start_time, path):
    return "{}/{}-wildlife.avi".format(path, start_time.strftime("%Y%m%d-%H%M%S"))


class Wildlife:
    """Wildlife"""

    def __init__(self, config):
        self.config = config
        self.exit_by_handler = False
        self.start_recording_threshold_t1 = None
        self.start_recording_threshold_t2 = None
        self.last_activity = None
        self.recording_status = "OFF"
        self.recording_color = (255, 255, 225)
        self.recording_info = ""
        self.recording_filename = ""
        self.start_recording_time = None
        self.stop_recording_time = None
        self.video_out = None
        self.activity_count_total = 0
        self.activity_count_during_recording = 0
        self.last_recording_snapshot = None
        self.notifier = None

    def signal_handler(self, signal_received, f):
        print('[INFO] SIGINT or CTRL-C detected. Exiting gracefully')
        self.exit_by_handler = True

    def start_recording_threshold(self, activity_count):
        if activity_count % 5 == 0:
            self.start_recording_threshold_t2 = self.start_recording_threshold_t1
            self.start_recording_threshold_t1 = datetime.datetime.now()
            if self.start_recording_threshold_t2 is not None and (
                    self.start_recording_threshold_t1 - self.start_recording_threshold_t2).seconds < 1:
                return True
        return False

    def writer_finished(self, file_name):
        if self.notifier is not None and self.last_recording_snapshot is not None:
            snapshot_filename = file_name.rsplit('.', 1)[0] + '.jpg'
            cv2.imwrite(snapshot_filename, self.last_recording_snapshot)
            self.notifier.send_message("New Wildlife Video: {}".format(os.path.basename(file_name)), snapshot_filename)

    def run(self):
        signal(SIGINT, self.signal_handler)

        # prepare video storage folder
        if os.path.exists(self.config.store_path) and self.config.clean_store_on_startup:
            shutil.rmtree(self.config.store_path)
        os.mkdir(self.config.store_path)

        if self.config.system == "raspberrypi":
            from capture_picamera import CapturePiCameraAsync as Capture
        else:
            from capture_opencv import CaptureOpencv as Capture

        self.notifier = None
        if self.config.telegram_notification:
            self.notifier = TelegramNotifier(self.config)

        capture = Capture(self.config)

        writer = AsyncVideoWriter(self.config, self.writer_finished)

        motion = MotionDetection(self.config)

        motion_detected = False
        motion_rectangles = [(0, 0, self.config.resolution[0], self.config.resolution[1])]

        capture.start()

        fps = FPS().start()

        frame_count = 0
        while True:
            frame, frame_timestamp = capture.read()

            if frame is None:
                continue

            frame_count += 1

            timestamp = datetime.datetime.now()

            if self.config.motion_detection and frame_count % 3 == 0:
                motion_detected, motion_rectangles = motion.detect_motion(frame)

            motion_status = "activity"
            motion_status_color = (255, 255, 255)
            if motion_detected:
                self.last_activity = datetime.datetime.now()
                self.activity_count_total += 1

                if self.recording_status == "OFF" and self.start_recording_threshold(self.activity_count_total):
                    self.recording_status = "ON"
                    self.recording_color = (0, 0, 255)
                    self.start_recording_time = frame_timestamp
                    self.recording_filename = create_video_filename(self.start_recording_time, self.config.store_path)
                    if self.config.store_video:
                        self.activity_count_during_recording = 0
                        writer.start(self.recording_filename)

                self.activity_count_during_recording += 1
                if self.activity_count_during_recording == self.config.store_activity_count_threshold + 1:
                    self.last_recording_snapshot = frame.copy()

                motion_status = "activity"
                motion_status_color = (0, 255, 0)
                if motion_rectangles is not None:
                    for r in motion_rectangles:
                        cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), motion_status_color, 1)

            if self.recording_status == "ON" and self.last_activity < timestamp and \
                    (timestamp - self.last_activity).seconds >= self.config.min_recording_time_seconds:
                if self.config.store_video:
                    writer.stop(self.activity_count_during_recording)
                self.recording_status = "OFF"
                self.recording_info = ""
                self.stop_recording_time = timestamp
                self.recording_color = (255, 255, 255)

            if self.config.store_video and self.recording_status == "ON":
                self.recording_info = " | " + self.recording_filename + " " + str(
                    (frame_timestamp - self.start_recording_time).seconds) + \
                                      " activity: " + str(self.activity_count_during_recording)

            timestamp_str = frame_timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
            cv2.putText(frame, motion_status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, motion_status_color, 2)
            cv2.putText(frame, self.recording_status, (frame.shape[1] - 50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                        self.recording_color, 2)
            cv2.putText(frame, timestamp_str + self.recording_info, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35
                        , (255, 255, 255), 1)

            # store frame
            if self.config.store_video:
                writer.write(frame)

            if self.config.show_video:
                cv2.imshow('captured frame', frame)
                if cv2.waitKey(1) == ord('q'):
                    break

            if self.exit_by_handler:
                break

            fps.update()

        # shutdown
        fps.stop()
        print("[INFO] elapsed time: {:.2f} s".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        writer.stop(0)
        capture.stop()
        if self.config.show_video:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", required=True,
                    help="path to the JSON configuration file")
    args = vars(ap.parse_args())

    app = Wildlife(WildlifeConfig(args["config"]))
    app.run()
