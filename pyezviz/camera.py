import time
import pyezviz.DeviceSwitchType
from pyezviz.DeviceSwitchType import DeviceSwitchType


KEY_ALARM_NOTIFICATION = 'globalStatus'

ALARM_SOUND_MODE= { 0 : 'Software',
                    1 : 'Intensive',
                    2 : 'Disabled',
}

class PyEzvizError(Exception):
    pass

class EzvizCamera(object):
    def __init__(self, client, serial):
        """Initialize the camera object."""
        self._serial = serial
        self._client = client
        
    def load(self):
        """Load object properties"""
        page_list = self._client.get_PAGE_LIST()

        # we need to know the index of this camera's self._serial  
        for device in page_list['deviceInfos']:
            if device['deviceSerial'] == self._serial :
                self._device = device
                break

        for camera in page_list['cameraInfos']:
            if camera['deviceSerial'] == self._serial :
                self._camera_infos = camera
                break

        # global status
        self._status = page_list['statusInfos'][self._serial]

        # load connection infos
        self._connection = page_list['connectionInfos'][self._serial]

        # # load switches
        self._switches = {}
        for switch in  page_list['switchStatusInfos'][self._serial]:
            self._switches[switch['type']] = switch['enable']

        # load detection sensibility
        self._detection_sensibility = self._client.get_detection_sensibility(self._serial)
        return True


    def status(self):
        """Return the status of the camera."""
        self.load()

        return {
            'serial': self._serial,
            'name': self._device['name'],
            'status': self._device['status'],
            'device_sub_category': self._device['deviceSubCategory'],

            'privacy': self._switches.get( DeviceSwitchType.SLEEP.value ),
            'audio': self._switches.get( DeviceSwitchType.SOUND.value ),
            'ir_led': self._switches.get( DeviceSwitchType.INFRARED_LIGHT.value ),
            'state_led': self._switches.get(DeviceSwitchType.LIGHT.value),
            'follow_move': self._switches.get(DeviceSwitchType.MOBILE_TRACKING.value),
            'outdoor_ringing_sound': self._switches.get(DeviceSwitchType.OUTDOOR_RINGING_SOUND.value),

            'alarm_notify': bool(self._status[KEY_ALARM_NOTIFICATION]),
            'alarm_sound_mod': ALARM_SOUND_MODE[int(self._status['alarmSoundMode'])],

            'encrypted': bool(self._status['isEncrypt']),

            'local_ip': self._connection['localIp'],
            'local_rtsp_port': self._connection['localRtspPort'],

            'detection_sensibility': self._detection_sensibility,
        }


    def move(self, direction, speed=5):
        """Moves the camera."""
        if direction not in ['right','left','down','up']:
            raise PyEzvizError("Invalid direction: %s ", direction)

        # launch the start command
        self._client.ptzControl(str(direction).upper(), self._serial, 'START', speed)
        # launch the stop command
        self._client.ptzControl(str(direction).upper(), self._serial, 'STOP', speed)

        return True

    def alarm_notify(self, enable):
        """Enable/Disable camera notification when movement is detected."""
        return self._client.data_report(self._serial, enable)

    def alarm_sound(self, sound_type):
        """Enable/Disable camera sound when movement is detected."""
        # we force enable = 1 , to make sound...
        return self._client.alarm_sound(self._serial, sound_type, 1)

    def alarm_detection_sensibility(self, sensibility):
        """Enable/Disable camera sound when movement is detected."""
        # we force enable = 1 , to make sound...
        return self._client.detection_sensibility(self._serial, sensibility)

    def switch(self, switch_type, enable=0):
        """Switch status on a device."""
        return self._client.switch_status(self._serial, switch_type, enable)
