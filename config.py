import json


class WildlifeConfig:
    """Wildlife Configuration"""

    def __init__(self, config_name):
        self.__config = json.load(open(config_name))

    @property
    def show_video(self):
        return self.__config["show_video"]

    @property
    def store_video(self):
        return self.__config["store_video"]

    @property
    def store_path(self):
        return self.__config["store_path"]

    @property
    def resolution(self):
        return tuple(self.__config["resolution"])

    @property
    def frame_rate(self):
        return self.__config["fps"]

    @property
    def delta_threshold(self):
        return self.__config["delta_threshold"]

    @property
    def min_area(self):
        return self.__config["min_area"]

    @property
    def min_recording_time_seconds(self):
        return self.__config["min_recording_time_seconds"]
