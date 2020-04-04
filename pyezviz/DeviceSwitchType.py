import enum
from enum import Enum, unique
@unique
class DeviceSwitchType(enum.IntEnum):
    ALARM_TONE = 1
    STREAM_ADAPTIVE = 2
    LIGHT = 3
    INTELLIGENT_ANALYSIS = 4
    LOG_UPLOAD = 5
    DEFENCE_PLAN = 6
    PRIVACY = 7
    SOUND_LOCALIZATION = 8
    CRUISE = 9
    INFRARED_LIGHT = 10
    WIFI = 11
    WIFI_MARKETING = 12
    WIFI_LIGHT = 13
    PLUG = 14
    # 15
    SLEEP = 21
    SOUND = 22
    BABY_CARE = 23
    LOGO = 24
    MOBILE_TRACKING = 25
    CHANNELOFFLINE = 26
    PTZ_AUTO_RESET = 28
    ALL_DAY_VIDEO = 29
    DOOR_REMINDER = 30
    AUTO_SLEEP = 32
    ROAMING_STATUS = 34
    DEVICE_4G_STATUS = 35
    ALARM_REMIND_MODE = 37
    # 38
    OUTDOOR_RINGING_SOUND = 39
    HUMAN_INTELLIGENT_DETECTION = 200
    RECEIVE_DOORBELL_CONTACT = 201
    FACE_SERVICE = 202
    # 300
    ALARM_LIGHT = 301
    HUMAN_FILTER = 302
    SECURITY_LIGHT = 303
    ALARM_LIGHT_RELEVANCE = 305
    CHILD_LOCK = 400
    BELL_SOUNDS = 450
    SCREEN_LIGHT = 500
    INDICATOR_LIGHT = 501
    DEVICE_ALARM_SOUND = 502
    OUTLET_RECOVER = 600
    HUMAN_TRACKING = 650
    CRUISE_TRACKING = 651
    PARTIAL_IMAGE_OPTIMIZE = 700

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return DeviceSwitchType[s.upper()]
        except KeyError:
            return s