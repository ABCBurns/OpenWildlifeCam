import cv2
import imutils


class MotionDetection:
    """Motion Detection"""

    def __init__(self, config):
        self.average_frame = None
        self.config = config
        self.frame_count = 0
        self.scale_ratio = self.config.resolution[0]/self.config.motion_detection_width

    def detect_motion(self, frame_input):
        motion_detected = False
        rect_list = []
        self.frame_count += 1

        # resize input frame, convert it to grayscale and blur it
        frame_capture = imutils.resize(frame_input, width=self.config.motion_detection_width)
        frame_gray = cv2.cvtColor(frame_capture, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.GaussianBlur(frame_gray, (21, 21), 0)

        # if the average frame is None, initialize it
        if self.average_frame is None:
            print("create initial average frame (background model)")
            self.average_frame = frame_gray.copy().astype("float")
            return motion_detected, rect_list

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
        frame_delta_thresh = cv2.dilate(frame_delta_thresh, None, iterations=2)

        # extract contours an draw them in the origin frame
        if self.config.show_video:
            contours = cv2.findContours(frame_delta_thresh.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours = cv2.findContours(frame_delta_thresh, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)

        contours = imutils.grab_contours(contours)

        # loop over the contours
        for c in contours:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < self.config.min_area:
                continue
            # create box around the contour and add it to return list
            motion_detected = True
            if self.config.motion_rectangle:
                rect_list.append(cv2.boundingRect(c))
            else:
                # faster detection path without motion detection frame
                break

        # combined_rectangles = rectangle.combine_rectangles(rect_list)
        # for r in combined_rectangles:
        #    cv2.rectangle(frame, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (0, 255, 0), 2)

        scaled_rect_list = []
        for r in rect_list:
            scaled_rect_list.append(
                (int(r[0] * self.scale_ratio), int(r[1] * self.scale_ratio),
                 int(r[2] * self.scale_ratio), int(r[3] * self.scale_ratio)))

        if self.config.show_video:
            # show the resulting frame
            cv2.drawContours(frame_gray, contours, -1, (0, 255, 0), 1)
            for r in rect_list:
                cv2.rectangle(frame_gray, (r[0], r[1]), (r[0] + r[2], r[1] + r[3]), (255, 255, 255), 1)
            cv2.imshow('prepared frame', frame_gray)
            cv2.imshow('frame delta', frame_delta_thresh)

        return motion_detected, scaled_rect_list
