import cv2
import imutils


class MotionDetection:
    """Motion Detection"""

    def __init__(self, config):
        self.average_frame = None
        self.config = config

    def detect_motion(self, frame_capture):
        rect_list = []

        # resize the frame, convert it to grayscale, and blur it
        # frame = imutils.resize(frame, width=500)
        frame_gray = cv2.cvtColor(frame_capture, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.GaussianBlur(frame_gray, (21, 21), 0)

        # frame = frame.array
        # if the average frame is None, initialize it
        if self.average_frame is None:
            print("starting background model...")
            self.average_frame = frame_gray.copy().astype("float")
            return rect_list

        # accumulate the weighted average between the current frame and
        # previous frames
        # accumulateWeighted(src, dst, alpha)
        # dst(x, y) = (1−alpha)⋅dst(x, y) + alpha⋅src(x, y)
        cv2.accumulateWeighted(frame_gray, self.average_frame, 0.5)

        # compute the difference between the current frame and running average
        frame_delta = cv2.absdiff(frame_gray, cv2.convertScaleAbs(self.average_frame))

        # create monochrome frame via threshold and dilate it
        frame_delta_thresh = cv2.threshold(frame_delta, self.config.delta_threshold, 255,
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
            if cv2.contourArea(c) < self.config.min_area:
                continue
            # create box around the contour and add it to return list
            rect_list.append(cv2.boundingRect(c))

        # combined_rectangles = rectangle.combine_rectangles(rect_list)
        # for r in combined_rectangles:
        #    cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (0, 255, 0), 2)

        if self.config.show_video:
            # show the resulting frame
            cv2.imshow('prepared frame', frame_gray)
            cv2.imshow('frame delta', frame_delta_thresh)
        return rect_list
