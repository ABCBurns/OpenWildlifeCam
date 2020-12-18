#!/usr/bin/env python
import time
import picamera


def record_video(seconds, resolution):
    with picamera.PiCamera() as camera:
        camera.resolution = resolution
        # camera.start_preview()
        time.sleep(2)
        start_time = time.perf_counter()
        camera.start_recording("record_video_{}x{}.h264".format(resolution[0], resolution[1]))
        camera.wait_recording(seconds)
        camera.stop_recording()
        stop_time = time.perf_counter()
        print("record_video: encoding/recording time: {:.2f} s".format(stop_time - start_time))


record_video(10, (1024, 768))

record_video(10, (800, 600))

record_video(10, (640, 480))
