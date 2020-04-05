import time
import pyezviz.DeviceSwitchType
from pyezviz.DeviceSwitchType import DeviceSwitchType
from pyezviz.DeviceMapSupport import DeviceMapSupport
import json
import asyncio
import binascii
import hashlib



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

        # load switches
        self._switches = {}
        for switch in  page_list['switchStatusInfos'][self._serial]:
            try:
                switchName = DeviceSwitchType(switch['type']).name
            except ValueError:
                switchName = switch['type']
            self._switches[switchName] = switch['enable']


        # load support-map
        self._support = {}
        supportExt = json.loads(self._device["supportExt"])
        for support in supportExt:
            try:
                supportName = DeviceMapSupport(int(support)).name
            except ValueError:
                supportName = support
            self._support[supportName] = supportExt[support]
            

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
            'switches' : self._switches,
            'support': self._support,

            'alarm_notify': bool(self._status[KEY_ALARM_NOTIFICATION]),
            'alarm_sound_mod': ALARM_SOUND_MODE[int(self._status['alarmSoundMode'])],

            'encrypted': bool(self._status['isEncrypt']),

            'local_ip': self._connection['localIp'],
            'local_rtsp_port': self._connection['localRtspPort'],
            'localCmdPort' : self._connection['localCmdPort'],
            'localStreamPort' : self._connection['localStreamPort'],

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

    def pack(self, magic, magic2, message):
        message = message.replace(" ","")
        msgln = (len(message)) // 2
        msgl = msgln.to_bytes(4, byteorder='big').hex()
        header = "9ebaace901000000000000" + magic + "00000000"+ magic2 + "ffffffff" + msgl + "00000000" 
        m = hashlib.md5()
        m.update(bytearray.fromhex(message))
        message = header + message + m.hexdigest().encode("utf-8").hex()
       
        return message

    async def stream(self):
         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("03", "00003003", 
                    "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
                    "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
                    "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
                    "f5 7c df 2e db 32 48 00 f4 e2 fd 17 8c 32 53 ac"
                    "7f 66 b9 6b 6c 3d 56 35 bf 35 96 24 dd 20 8a 2c"
                    "53 6b 55 3f 56 f8 92 b7 8f 57 55 89 1e 6a d9 e6"
                    "ce 30 d1 b3 a3 d3 9a fe cc 11 88 6a de 2f cb 8f")
                    
         cmdwriter.write(bytearray.fromhex(message))
         await cmdwriter.drain()
         print('reading3:')
         data = await cmdreader.read(-1)
         print(f'Received3: {bytes.hex(data)}')
         cmdwriter.close()
         await cmdwriter.wait_closed()

         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("04", "00003003", 
                    "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
                    "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
                    "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
                    "f5 7c df 2e db 32 48 00 f4 e2 fd 17 8c 32 53 ac"
                    "7f 66 b9 6b 6c 3d 56 35 bf 35 96 24 dd 20 8a 2c"
                    "53 6b 55 3f 56 f8 92 b7 8f 57 55 89 1e 6a d9 e6"
                    "ce 30 d1 b3 a3 d3 9a fe cc 11 88 6a de 2f cb 8f")
         cmdwriter.write(bytearray.fromhex(message))
         await cmdwriter.drain()
         data = await cmdreader.read(-1)
         print(f'Received4: {bytes.hex(data)}')
         cmdwriter.close()
         await cmdwriter.wait_closed()

         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("06", "00002011", 
            "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
            "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
            "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
            "f5 7c df 2e db 32 48 00 f4 e2 fd 17 8c 32 53 ac"
            "7f 66 b9 6b 6c 3d 56 35 bf 35 96 24 dd 20 8a 2c"
            "63 4c 4a 0a 2f b5 a1 6e 6a 2e c7 05 1f 96 36 7a"
            "80 a0 93 f8 f7 4f 12 3c 92 df 3a 31 97 bf 59 e8"
            "b9 32 02 7a 1f 00 7a 35 3e 19 0f 2c 0c 6c 49 f1"
            "f3 38 38 0b 8c 29 0c 59 36 f6 2a 20 ca d5 a9 03"
            "b7 a7 5f de 2a 64 fb 4e f3 b9 3d 88 61 67 ed 3a"
            "fe 12 29 f2 5d 98 a5 3f 2f 42 01 91 1a e0 86 ae"
            "68 6c c1 ba de 77 28 54 8b 05 8e d4 c8 45 90 44"
            "c6 5d 35 17 af 26 61 2d 35 22 5f 24 a3 43 7a 5e"
            "70 0c f6 13 ad f7 7d 28 a3 05 dc 38 0f 48 04 97"
            "d0 2e 0b 99 e5 a1 6f f5 83 de ed 78 c2 e2 a5 ce")            
            
         cmdwriter.write(bytearray.fromhex(message))
         await cmdwriter.drain()
         data = await cmdreader.read(-1)
         print(f'Received2: {bytes.hex(data)}')

         cmdwriter.close()
         await cmdwriter.wait_closed()


         stmreader, stmwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localStreamPort']))
         stmmessage = self.pack("07", "00003105", 
            "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
            "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
            "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
            # I don't know how to encode the following part. The difference is significant everytime. Maybe sth like hashed sessionid?
            "3f 05 95 09 a7 96 f5 13 e0 f1 6c 69 9b 94 4a 29" 
            "e9 aa 4a d8 a2 0d 54 dc 3a f9 40 99 84 b6 57 3c"
            "59 25 81 a6 28 bf 9e 9d 95 5d 7c 8a 44 95 d7 92"
            "13 28 85 f9 7b 62 1b b6 26 2e 28 1f 8c a2 8f c5")
         
         print (stmmessage)
         stmwriter.write(bytearray.fromhex(stmmessage))
         await stmwriter.drain()
         data = await stmreader.read(-1)
         print(f'Received10: {bytes.hex(data)}')

         # The following error is returned:
         # <?xml version="1.0" encoding="utf-8"?>
         # <Response>
         #   <Result>129</Result>
         # </Response>


         stmwriter.close()
         await stmwriter.wait_closed()
         

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
