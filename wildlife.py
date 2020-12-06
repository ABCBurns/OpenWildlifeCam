#!/usr/bin/env python

# construct the argument parser and parse the arguments
import argparse
import json
import numpy as np
import cv2 as cv

# read config
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=True,
                help="path to the JSON configuration file")
args = vars(ap.parse_args())
config = json.load(open(args["config"]))
resolution = tuple(config["resolution"])
frame_rate = config["fps"]

# capture video
cap = cv.VideoCapture(0)

# set the width and height, and UNSUCCESSFULLY set the exposure time
cap.set(cv.CAP_PROP_FRAME_WIDTH, resolution[0])
cap.set(cv.CAP_PROP_FRAME_HEIGHT, resolution[1])
cap.set(cv.CAP_PROP_FPS, frame_rate)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("can't read frame")
        break
    # create gray image of the frame
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # show the resulting frame
    cv.imshow('frame', gray)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
