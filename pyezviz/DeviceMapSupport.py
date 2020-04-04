import enum
from enum import Enum, unique
@unique
class DeviceMapSupport(enum.IntEnum):
    Defence = 1
    Talk = 2
    DefencePlan = 3
    Disk = 4
    Privacy = 5
    Message = 6
    AlarmVoice = 7
    AutoOffline = 8
    Encrypt = 9
    Upgrade = 10
    Cloud = 11
    CloudVersion = 12
    Wifi = 13
    Capture = 14
    ChangeSafePasswd = 15
    Resolution = 16
    MultiScreen = 17
    UploadCloudFile = 18
    AddDelDetector = 19
    IpcLink = 20
    ModifyDetectorname = 21
    SafeModePlan = 22
    ModifyDetectorguard = 23
    Weixin = 24
    Ssl = 25
    RelatedDevice = 26
    RelatedStorage = 27
    RemoteAuthRandcode = 28
    SdkTransport = 29
    PtzTopBottom = 30
    PtzLeftRight = 31
    Ptz45Degree = 32
    PtzZoom = 33
    Preset = 34
    PtzCommonCruise = 35
    PtzFigureCruise = 36
    PtzCenterMirror = 37
    PtzLeftRightMirror = 38
    PtzTopBottomMirror = 39
    PtzPrivacy = 40
    Wifi24G = 41
    Wifi5G = 42
    WifiPortal = 43
    Unbind = 44
    AutoAdjust = 45
    Timezone= 46
    Language = 47
    CloseInfraredLight = 48
    ModifyChanName = 49
    PtzModel = 50
    TalkType = 51
    ChanType = 52
    FlowStatistics = 53
    More = 54
    RemoteQuiet = 55
    Bluetooth = 58
    PreP2P = 59
    Microscope = 60
    SensibilityAdjust = 61
    Sleep = 62
    AudioOnoff = 63
    ProtectionMode = 64
    RateLimit = 65
    Music = 67
    ReplaySpeed = 68
    ReverseDirect = 69
    ChannelOffline = 70
    PresetAlarm = 72
    IntelligentTrack = 73
    KeyFocus = 74
    VolumnSet = 75
    TemperatureAlarm = 76
    MicroVolumnSet = 77
    UnLock = 78
    NoencriptViaAntProxy = 79
    FullScreenPtz = 81
    NatPass = 84
    NewTalk = 87
    FulldayRecord = 88
    FishEye = 91
    CustomVoice = 92
    ReplayChanNums = 94
    HorizontalPanoramic = 95
    ActiveDefense = 96
    MotionDetection = 97
    PtzFocus = 99
    PirDetect = 100
    DoorbellTalk = 101
    RestartTime = 103
    ApMode = 106
    VerticalPanoramic = 112
    AlarmLight = 113
    Chime = 115
    RelationCamera = 117
    PirSetting = 118
    BatteryManage = 119
    AutoSleep = 144
    Isapi = 145
    QuickplayWay = 149
    Ptz = 154
    BellSet = 164
    AudioCollect = 165
    PtzcmdViaP2pv3 = 169
    AbsenceReminder = 181   
    DeviceRing = 185 
    SwitchLog = 187
    IndicatorBrightness = 188
    PoweroffRecovery = 189
    Call = 191
    ChannelTalk = 192
    SimCard = 194
    FaceFrameMark = 196
    Tracking = 198
    ChangeVolume = 203
    NightVisionMode = 206
    TimeSchedulePlan = 209
    SoundLightAlarm = 214
    AlertTone = 215
    Devicelog = 216
    DisturbMode = 217
    DevicePowerMessage = 218
    PartialImageOptimize = 221
    DetectHumanCar = 224
    EnStandard = 235
    MultiSubsys = 255
    ReplayDownload = 260
    ServerSideEncryption = 261
    SmartNightVision = 274
    DisturbNewMode = 292
    DetectMoveHumanCar = 302
    BackLight = 303
    EzvizChime = 380


    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return DeviceMapSupport[s.upper()]
        except KeyError:
            return s