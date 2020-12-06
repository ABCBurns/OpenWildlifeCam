#!/usr/bin/env python

# construct the argument parser and parse the arguments
import argparse
import json

import imutils
import numpy as np
import cv2

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

# capture video
average_frame = None
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
    ret, frame_capture = cap.read()
    if not ret:
        print("can't read frame")
        break

    # resize the frame, convert it to grayscale, and blur it
    # frame = imutils.resize(frame, width=500)
    frame_gray = cv2.cvtColor(frame_capture, cv2.COLOR_BGR2GRAY)
    frame_gray = cv2.GaussianBlur(frame_gray, (21, 21), 0)

    # frame = frame.array
    # if the average frame is None, initialize it
    if average_frame is None:
        print("[INFO] starting background model...")
        average_frame = frame_gray.copy().astype("float")
        # frame.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames
    # accumulateWeighted(src, dst, alpha)
    # dst(x, y) = (1−alpha)⋅dst(x, y) + alpha⋅src(x, y)
    cv2.accumulateWeighted(frame_gray, average_frame, 0.5)

    # compute the difference between the current frame and running average
    frame_delta = cv2.absdiff(frame_gray, cv2.convertScaleAbs(average_frame))

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
        # create and draw bounding box around the contour
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame_capture, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # show the resulting frame
    cv2.imshow('captured frame', frame_capture)
    cv2.imshow('prepared frame', frame_gray)
    cv2.imshow('frame delta', frame_delta_thresh)
    if cv2.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
