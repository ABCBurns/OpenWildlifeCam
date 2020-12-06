#!/usr/bin/env python

# construct the argument parser and parse the arguments
import argparse
import json
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
    ret, capture_frame = cap.read()
    if not ret:
        print("can't read frame")
        break


    # resize the frame, convert it to grayscale, and blur it
    #frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(capture_frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    #frame = frame.array
    # if the average frame is None, initialize it
    if average_frame is None:
        print("[INFO] starting background model...")
        average_frame = gray.copy().astype("float")
        #frame.truncate(0)
        continue

    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    cv2.accumulateWeighted(gray, average_frame, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(average_frame))

    # show the resulting frame
    cv2.imshow('frame', gray)
    cv2.imshow('frameDelta', frameDelta)
    if cv2.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
