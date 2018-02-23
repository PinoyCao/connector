# -*- coding: UTF-8 -*-
import logging
import subprocess
import copy
from settings import ADB_COMMAND


logging.basicConfig(
    format="[scan %(asctime)s] %(levelname)s %(message)s",
    level=logging.INFO)

PLATFORM_IOS = 1
PLATFORM_ANDROID = 2

DEVICE_TYPE_SIMULATOR = 1
DEVICE_TYPE_REAL_DEVICE = 2


'''scan for local android devices using adb
Will check if adb is installed and device is authorized
Create new device if a new udid occur or use captured information
'''


class ScanDevice(object):
    @classmethod
    def scan(cls):
        devices = []
        # check if adb is installed
        if subprocess.call(ADB_COMMAND+' start-server'):
            raise Exception('adb start-server failed')

        output = subprocess.check_output(ADB_COMMAND+' devices -l')

        lines = [i for i in output.split('\r\n') if i]
        lines.pop(0)   # title poped

        for line in lines:
            line = [i for i in line.split(' ') if i]
            # unauthorized device
            if len(line) == 2:
                status = line[1]
                if status == 'unauthorized':
                    logging.warn('Please enable USB debugging on yout device !')
		elif status == 'offline':
		    logging.warn('Lose connection with the device %s ' % line[0])
                else:
                    raise Exception('unknown error with device %s, abort!' % line[0])
            # authorized device with description
            else:
                udid = line.pop(0)
                model = cls.get_prop_for_android(udid, 'ro.product.model')
                version = cls.get_prop_for_android(udid, 'ro.build.version.release')
                brand = cls.get_prop_for_android(udid, 'ro.product.manufacturer')
                size = subprocess.check_output(ADB_COMMAND+' -s %s shell wm size'
                                               % udid).split(' ').pop(2).strip('\r\n')
                # detail = cls.get_prop.for_android(udid, '')
                #     create_time = time.strftime("%a, %d %b %Y %H:%M:%S -0000", time.localtime())
                device = cls.create_device(
                    udid=udid, device_type=DEVICE_TYPE_REAL_DEVICE,
                    platform=PLATFORM_ANDROID, brand=brand.capitalize(),
                    model=model, version=version,
                    name=model, is_auth=True, size=size,
                )
                devices.append(device)
        print devices
        return devices

    @staticmethod
    def create_device(platform, udid, device_type, model='', brand='', version='', name='', is_auth=False, size=''):
        device = copy.deepcopy(DEVICE_TEMPLATE)
        device['model']['platform'] = platform
        device['model']['brand'] = brand
        device['model']['name'] = model
        device['model']['point'] = size
        device['model']['pixel'] = size
        device['udid'] = udid
        device['version'] = version
        device['type'] = device_type
        device['name'] = name
        device['is_auth'] = is_auth
        return device

    @staticmethod
    def get_prop_for_android(udid, key):
        return subprocess.check_output(
            ADB_COMMAND+' -s %s shell getprop %s' % (udid, key)).strip('\r\n')


DEVICE_TEMPLATE = {
            "is_auth": False,
            "name": "device-name",
            "udid": "udid-template",
            "version": "",
            "model": {
                "platform": 2,
                "brand": "",
                "name": "",
                "point": "",
                "pixel": ""
            },
            "type": 2,
            "detail": ""
        }


if __name__ == '__main__':
    print ScanDevice.scan()
