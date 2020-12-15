#!/usr/bin/env python

import argparse
import datetime
import os
import shutil
import cv2
from signal import signal, SIGINT

import imutils
from imutils.video import FPS

from config import WildlifeConfig
from motion import MotionDetection
from video_writer import AsyncVideoWriter

exit_by_handler = False


def signal_handler(signal_received, f):
    global exit_by_handler
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit_by_handler = True


def create_video_filename(start_time, path):
    return "{}/{}-wildlife.avi".format(path, start_time.strftime("%Y%m%d-%H%M%S"))


last_activity = None
recording_status = "OFF"
recording_color = (255, 255, 225)
recording_info = ""
recording_filename = ""
start_recording_time = None
stop_recording_time = None
video_out = None

signal(SIGINT, signal_handler)

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True,
                help="path to the JSON configuration file")
args = vars(ap.parse_args())

config = WildlifeConfig(args["config"])

# prepare video storage folder
if config.clean_store_on_startup:
    shutil.rmtree(config.store_path)
os.mkdir(config.store_path)

if config.system == "raspberrypi":
    # from capture_picamera import CapturePiCamera as Capture
    from capture_picamera_threaded import CapturePiCameraThreaded as Capture
else:
    from capture_opencv import CaptureOpencv as Capture

capture = Capture(config)

writer = AsyncVideoWriter(config)

md = MotionDetection(config)

motion_rectangles = [(0, 0, config.resolution[0], config.resolution[1])]

capture.start()

fps = FPS().start()

frame_count = 0
while True:
    frame = capture.read()

    if frame is None:
        continue

    frame_count += 1

    timestamp = datetime.datetime.now()

    if config.motion_detection and frame_count % 3 == 0:
        motion_rectangles = md.detect_motion(frame)

    motion_status = "no activity"
    motion_status_color = (255, 255, 255)
    for r in motion_rectangles:
        last_activity = datetime.datetime.now()
        if recording_status == "OFF":
            start_recording_time = timestamp
            recording_filename = create_video_filename(start_recording_time, config.store_path)
            if config.store_video:
                writer.start(recording_filename)

        recording_status = "ON"
        recording_color = (0, 0, 255)
        motion_status = "activity"
        motion_status_color = (0, 255, 0)
        cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), motion_status_color, 1)

    if recording_status == "ON" and last_activity < timestamp and \
            (timestamp - last_activity).seconds >= config.min_recording_time_seconds:
        if config.store_video:
            writer.stop()
        recording_status = "OFF"
        recording_info = ""
        stop_recording_time = timestamp
        recording_color = (255, 255, 255)

    if config.store_video and recording_status == "ON":
        recording_info = " | " + recording_filename + " " + str((timestamp - start_recording_time).seconds)

    timestamp_str = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, motion_status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, motion_status_color, 2)
    cv2.putText(frame, recording_status, (frame.shape[1] - 50, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, recording_color, 2)
    cv2.putText(frame, timestamp_str + recording_info, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35
                , (255, 255, 255), 1)

    # store frame
    if config.store_video:
        writer.write(frame)

    if config.show_video:
        cv2.imshow('captured frame', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    if exit_by_handler:
        break

    fps.update()

# shutdown
fps.stop()
print("elapsed time: {:.2f} s".format(fps.elapsed()))
print("approx. FPS: {:.2f}".format(fps.fps()))
writer.stop()
capture.stop()
if config.show_video:
    cv2.destroyAllWindows()
