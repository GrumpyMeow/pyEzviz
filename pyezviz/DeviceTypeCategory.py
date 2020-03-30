import enum
from enum import Enum, unique
@unique
class DeviceTypeCategory(Enum):
    AlarmBox = "AlarmBox"
    BDoorBell = "BDoorBell"
    BatteryCamera = "BatteryCamera"
    CatEye = "CatEye"
    DBChime = "DBChime"
    DVR = "DVR"
    Detector = "Detector"
    DoorLock = "DoorLock"
    IPC = "IPC"
    NVR = "NVR"
    Router = "Router"
    RouterW3 = "RouterW3"
    RouterW5 = "RouterW5"
    Socket = "Socket"
    WirelessDoorbell = "Wireless Doorbell"
    XVR = "XVR"
