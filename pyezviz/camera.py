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
        # magic = message sequence (increments each request)
        # magic2 = command code ?
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
         data = await cmdreader.read(-1)
         print(f'3003 Recv: {bytes.hex(data)}')
         cmdwriter.close()
         await cmdwriter.wait_closed()


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
         data = await cmdreader.read(-1)
         print(f'3003-2 Recv : {bytes.hex(data)}')
         cmdwriter.close()
         await cmdwriter.wait_closed()

         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("03", "00003201", 
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
         print(f'3201 Recv: {bytes.hex(data)}')
         cmdwriter.close()
         await cmdwriter.wait_closed()

         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("03", "00003201", 
                    "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
                    "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
                    "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
                    "f5 7c df 2e db 32 48 00 f4 e2 fd 17 8c 32 53 ac"
                    "7f 66 b9 6b 6c 3d 56 35 bf 35 96 24 dd 20 8a 2c"
                    "63 4c 4a 0a 2f b5 a1 6e 6a 2e c7 05 1f 96 36 7a"
                    "e0 19 e7 ef 01 9a 65 f4 d6 e1 50 e5 bd dd f2 8b"
                    "44 30 9a bf f8 33 de 05 d1 02 67 67 00 77 3d a7"
                    "4c 43 95 8e 05 e8 39 56 90 27 6c 44 9d 73 71 c0"
                    "5e d3 84 13 eb 89 77 73 d8 c9 17 4b c7 15 df 18"
                    "6b db 05 04 c5 60 fa ca 93 08 06 01 f5 34 24 73")
         cmdwriter.write(bytearray.fromhex(message))
         await cmdwriter.drain()
         data = await cmdreader.read(-1)
         print(f'3201-2 Recv: {bytes.hex(data)}')
         #<?xml version="1.0" encoding="utf-8"?><Response><Result>0</Result><Day list="20,21,22,25,26,27,28,2 9,30,31"/></Response>
         cmdwriter.close()
         await cmdwriter.wait_closed()

         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("03", "00003201", 
                    "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
                    "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
                    "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
                    "f5 7c df 2e db 32 48 00 f4 e2 fd 17 8c 32 53 ac"
                    "7f 66 b9 6b 6c 3d 56 35 bf 35 96 24 dd 20 8a 2c"
                    "63 4c 4a 0a 2f b5 a1 6e 6a 2e c7 05 1f 96 36 7a"
                    "e0 19 e7 ef 01 9a 65 f4 d6 e1 50 e5 bd dd f2 8b"
                    "44 30 9a bf f8 33 de 05 d1 02 67 67 00 77 3d a7"
                    "4c 43 95 8e 05 e8 39 56 90 27 6c 44 9d 73 71 c0"
                    "d5 27 d8 0f a6 31 ec 6f 80 62 32 70 db a2 e6 58"
                    "97 0c ec a4 8f dd 83 66 ee 49 e4 3b c2 46 95 2f")
         cmdwriter.write(bytearray.fromhex(message))
         await cmdwriter.drain()
         data = await cmdreader.read(-1)
         print(f'3201-3 Recv: {bytes.hex(data)}')
         #<?xml version="1.0" encoding="utf-8"?><Response><Result>0</Result><Day list="1,2,3,4,5"/></Response>
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
         print(f'3003 Recv: {bytes.hex(data)}')
         cmdwriter.close()
         await cmdwriter.wait_closed()

         cmdreader, cmdwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localCmdPort']))
         message = self.pack("0b", "00002013", 
                    "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
                    "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
                    "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
                    "f5 7c df 2e db 32 48 00 f4 e2 fd 17 8c 32 53 ac"
                    "7f 66 b9 6b 6c 3d 56 35 bf 35 96 24 dd 20 8a 2c"
                    "21 f2 f2 8b 08 83 23 d3 bd 84 3c 53 ab 73 d9 1d"
                    "b5 7b 93 71 6c f7 01 67 ef c1 a8 57 cf 03 82 43"
                    "57 0d 1a 79 a3 4f e4 fc 45 e7 8d 72 26 05 46 f3")
         cmdwriter.write(bytearray.fromhex(message))
         await cmdwriter.drain()
         data = await cmdreader.read(-1)
         print(f'2013 Recv: {bytes.hex(data)}')
         # <?xml version="1.0" encoding="utf-8"?><Response><Result>0</Result></Response>
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
         print(f'2011 Recv: {bytes.hex(data)}')
         # <?xml version="1.0" encoding="utf-8"?><Response><Result>0</Result><Session>10042</Session><StreamHeader Base64Data="SU1LSAEBAAACAAABASABEIA+AAAAfQAAAAAAAAAAAAAAAAAAAAAAAA==" Base64Length="56"/></Response>
         cmdwriter.close()
         await cmdwriter.wait_closed()

         stmreader, stmwriter = await asyncio.open_connection(self._connection['localIp'], int(self._connection['localStreamPort']))
         stmmessage = self.pack("07", "00003105", 
            "ba 65 f1 e8 d1 fa a3 db 46 fe 9f 6a ff a2 e3 e1"
            "02 2e 8c ba b7 e7 8c 49 eb 27 1c d4 7a f2 fd e3"
            "10 f1 6c f1 03 1d 44 77 f4 7f d7 00 6c a7 a8 26"
            # I don't know how to encode the following part. The difference is significant everytime. Maybe sth like hashed sessionid or time dependent?
            # The magic is done in "ezstreamclient" /EZStreamSDKJNA/ IClient.java / createCASClient / generateECDHKey
            # ezstream_generateECDHKey  zstream_setClientECDHKey
            # Ezviz uses Entrust certificates (are embedded in APK)
            # https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman
            "3f 05 95 09 a7 96 f5 13 e0 f1 6c 69 9b 94 4a 29" 
            "e9 aa 4a d8 a2 0d 54 dc 3a f9 40 99 84 b6 57 3c"
            "59 25 81 a6 28 bf 9e 9d 95 5d 7c 8a 44 95 d7 92"
            "13 28 85 f9 7b 62 1b b6 26 2e 28 1f 8c a2 8f c5")
         
         print ("3105 Send: " + stmmessage)
         stmwriter.write(bytearray.fromhex(stmmessage))
         await stmwriter.drain()
         data = await stmreader.read(-1)
         print(f'3105 Recv: {bytes.hex(data)}')
         # <?xml version="1.0" encoding="utf-8"?><Response><Result>129</Result></Response>
         stmwriter.close()
         await stmwriter.wait_closed()


         stmreader, stmwriter = await asyncio.open_connection(self._connection['localIp'], 8000)
         stmmessage = (
            "00 00 00 2c 63 00 00 00  79 ce fc 2b 00 03 00 00"
            "67 0b a8 c0 71 5f 0f bf  00 6b 9e 06 15 f7 00 00"
            "00 00 00 01 00 00 00 00  00 00 04 01")         

            # open.ys7.com ?

            # 00 00 00 2c 63 00 00 00  7a ea 71 36 00 03 00 00
            # 67 0b a8 c0 4d ab f4 69  00 6b 9e 06 15 f7 00 00
            # 00 00 00 01 00 00 00 00  00 00 04 01

            # 00 00 00 2c 63 00 00 00  17 a1 c9 98 00 03 00 00
            # 67 0b a8 c0 10 15 c0 a7  00 6b 9e 06 15 f7 00 00
            # 00 00 00 01 00 00 00 00  00 00 04 01   

            # 22:51 05-04-2020
            # 00 00 00 2c 63 00 00 00  79 f0 46 43 00 03 00 00
            # 67 0b a8 c0 0f 16 b2 82  00 6b 9e 06 15 f7 00 00
            # 00 00 00 01 00 00 00 00  00 00 04 01 
            
            # 22:54  05-04-2020
            # 00 00 00 2c 63 00 00 00  48 2f 4d fe 00 03 00 00 
            # 67 0b a8 c0 48 1c 01 a2  00 6b 9e 06 15 f7 00 00  
            # 00 00 00 01 00 00 00 00  00 00 04 01              

            # 23:21  05-04-2020 1,2,3
            # 00 00 00 2c 63 00 00 00  ce bf f3 e5 00 03 00 00 
            # 67 0b a8 c0 58 89 fd 0b  00 6b 9e 06 15 f7 00 00 
            # 00 00 00 01 00 00 00 00  00 00 04 01             
            # 00 00 00 2c 63 00 00 00  e6 b4 2c cc 00 03 00 00   
            # 67 0b a8 c0 72 25 9b 67  00 6b 9e 06 15 f7 00 00   
            # 00 00 00 01 00 00 00 00  00 00 04 01
            # 00 00 00 2c 63 00 00 00  5e 3f fc 4c 00 03 00 00
            # 67 0b a8 c0 59 8a 78 2e  00 6b 9e 06 15 f7 00 00
            # 00 00 00 01 00 00 00 00  00 00 04 01            


         stmwriter.write(bytearray.fromhex(stmmessage))
         await stmwriter.drain()
         data = await stmreader.read(-1)
         print(f'Recv: {bytes.hex(data)}')
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
