#!/usr/bin/env python

# construct the argument parser and parse the arguments
import argparse
import datetime
import json
import rectangle

import imutils
import numpy as np
import cv2


class MotionDetection:
    """Motion Detection"""

    def __init__(self):
        self.average_frame = None

    def detect_motion(self, frame_capture):
        rect_list = []

        # resize the frame, convert it to grayscale, and blur it
        # frame = imutils.resize(frame, width=500)
        frame_gray = cv2.cvtColor(frame_capture, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.GaussianBlur(frame_gray, (21, 21), 0)

        # frame = frame.array
        # if the average frame is None, initialize it
        if self.average_frame is None:
            print("[INFO] starting background model...")
            self.average_frame = frame_gray.copy().astype("float")
            # frame.truncate(0)
            return rect_list

        # accumulate the weighted average between the current frame and
        # previous frames
        # accumulateWeighted(src, dst, alpha)
        # dst(x, y) = (1−alpha)⋅dst(x, y) + alpha⋅src(x, y)
        cv2.accumulateWeighted(frame_gray, self.average_frame, 0.5)

        # compute the difference between the current frame and running average
        frame_delta = cv2.absdiff(frame_gray, cv2.convertScaleAbs(self.average_frame))

        # create monochrome frame via threshold and dilate it
        frame_delta_thresh = cv2.threshold(frame_delta, delta_threshold, 255,
                                           cv2.THRESH_BINARY)[1]
        frame_delta_thresh = cv2.dilate(frame_delta_thresh, None, iterations=5)

        # extract contours an draw them in the origin frame
        contours = cv2.findContours(frame_delta_thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        cv2.drawContours(frame_gray, contours, -1, (0, 255, 0), 1)

        # loop over the contours
        for c in contours:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < min_area:
                continue
            # create box around the contour and add it to return list
            rect_list.append(cv2.boundingRect(c))

        # combined_rectangles = rectangle.combine_rectangles(rect_list)
        # for r in combined_rectangles:
        #    cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (0, 255, 0), 2)

        # show the resulting frame
        cv2.imshow('prepared frame', frame_gray)
        cv2.imshow('frame delta', frame_delta_thresh)
        return rect_list


# read config
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True,
                help="path to the JSON configuration file")
args = vars(ap.parse_args())
config = json.load(open(args["config"]))
resolution = tuple(config["resolution"])
frame_rate = config["fps"]
delta_threshold = config["delta_thresh"]
min_area = config["min_area"]
min_recording_time_seconds = config["min_recording_time_seconds"]

md = MotionDetection()

# capture video
average_frame = None
is_recording = False
last_activity = None
recording_status = "OFF"
recording_color=(255,255,225)

cap = cv2.VideoCapture(0)

# set the width and height, and UNSUCCESSFULLY set the exposure time
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv2.CAP_PROP_FPS, frame_rate)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("can't read frame")
        break

    timestamp = datetime.datetime.now()

    motion_rectangles = md.detect_motion(frame)

    motion_status = "no activity"
    motion_status_color = (255, 255, 255)
    for r in motion_rectangles:
        last_activity = datetime.datetime.now()
        recording_status = "ON"
        recording_color = (0, 0, 255)
        motion_status = "activity"
        motion_status_color = (0, 255, 0)
        cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), motion_status_color, 1)

    if recording_status == "ON" and last_activity < timestamp and \
            (timestamp - last_activity).seconds >= min_recording_time_seconds:
        recording_status = "OFF"
        recording_color = (255, 255, 255)

    timestamp_str = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(frame, motion_status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, motion_status_color, 2)
    cv2.putText(frame, recording_status, (frame.shape[1] - 30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, recording_color, 2)
    cv2.putText(frame, timestamp_str, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)

    cv2.imshow('captured frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
