import argparse
import sys
import json
import logging
import pandas
from http.client import HTTPConnection


from pyezviz import EzvizClient, EzvizCamera
from pyezviz.DeviceSwitchType import DeviceSwitchType


def main():
    """Main function"""
    parser = argparse.ArgumentParser(prog='pyezviz')
    parser.add_argument('-u', '--username', required=True, help='Ezviz username')
    parser.add_argument('-p', '--password', required=True, help='Ezviz Password')
    parser.add_argument('--debug', '-d', action='store_true', help='Print debug messages to stderr')

    subparsers = parser.add_subparsers(dest='action')


    parser_device = subparsers.add_parser('devices', help='Play with all devices at once')
    parser_device.add_argument('device_action', type=str,
                        default='status', help='Device action to perform', choices=['device','status','switch','connection','switch-all'])


    parser_camera = subparsers.add_parser('camera', help='Camera actions')
    parser_camera.add_argument('--serial', required=True, help='camera SERIAL')

    subparsers_camera = parser_camera.add_subparsers(dest='camera_action')

    parser_camera_status = subparsers_camera.add_parser('status', help='Get the status of the camera')
    
    parser_camera_move = subparsers_camera.add_parser('move', help='Move the camera')
    parser_camera_move.add_argument('--direction', required=True, help='Direction to move the camera to', choices=['up','down','right','left'])
    parser_camera_move.add_argument('--speed', required=False, help='Speed of the movement', default=5, type=int, choices=range(1, 10))


    parser_camera_switch = subparsers_camera.add_parser('switch', help='Change the status of a switch')
    parser_camera_switch.add_argument('--switch', required=True, help='Switch to switch', type=DeviceSwitchType.argparse , choices=list(DeviceSwitchType), default=None )
    parser_camera_switch.add_argument('--enable', required=False, help='Enable (or not)', default=1, type=int, choices=[0,1] )

    parser_camera_alarm = subparsers_camera.add_parser('alarm', help='Configure the camera alarm')
    parser_camera_alarm.add_argument('--notify', required=False, help='Enable (or not)', default=0, type=int, choices=[0,1] )
    parser_camera_alarm.add_argument('--sound', required=False, help='Sound level (2 is disabled, 1 intensive, 0 software)', type=int, choices=[0,1,2])
    parser_camera_alarm.add_argument('--sensibility', required=False, help='Sensibility level (form 1 to 6)', default=3, type=int, choices=[0,1,2,3,4,5,6] )


    args = parser.parse_args()

    client = EzvizClient(args.username, args.password)

    if args.debug:

        log = logging.getLogger('urllib3')
        log.setLevel(level=logging.DEBUG)

        # logging from urllib3 to console
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        log.addHandler(ch)

        HTTPConnection.debuglevel = 1



    if args.action == 'devices':

        if args.device_action == 'device':
            try:
                client.login()
                print(json.dumps(client.get_DEVICE(), indent=2))
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        if args.device_action == 'status':
            try:
                client.login()
                # print(json.dumps(client.load_cameras(), indent=2))
                print(pandas.DataFrame(client.load_cameras()))
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        if args.device_action == 'switch':
            try:
                client.login()
                print(json.dumps(client.get_SWITCH_STATUS(), indent=2))
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        elif args.device_action == 'connection':
            try:
                client.login()
                print(json.dumps(client.get_CONNECTION(), indent=2))
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        elif args.device_action == 'switch-all':
            try:
                client.login()
                print(json.dumps(client.switch_devices(args.enable), indent=2))
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()


    elif args.action == 'camera':

        # load camera object
        try:
            client.login()
            camera = EzvizCamera(client, args.serial)
            logging.debug("Camera loaded")
        except BaseException as exp:
            print(exp)
            return 1


        if args.camera_action == 'move':
            try:
                camera.move(args.direction, args.speed)
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        elif args.camera_action == 'status':
            try:
                print(json.dumps(camera.status(), indent=2))

            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        elif args.camera_action == 'switch':
            try:
                camera.switch( args.switch , args.enable)
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()

        elif args.camera_action == 'alarm':
            try:
                if args.sound:
                        camera.alarm_sound(args.sound)
                if args.notify:
                        camera.alarm_notify(args.notify)
                if args.sensibility:
                        camera.alarm_detection_sensibility(args.sensibility)
            except BaseException as exp:
                print(exp)
                return 1
            finally:
                client.close_session()
    else:
        print("Action not implemented: %s", args.action)

if __name__ == '__main__':
    sys.exit(main())


