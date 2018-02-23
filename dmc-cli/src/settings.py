# -*- coding: UTF-8 -*-
import ConfigParser
import os
import io
import json

config = ConfigParser.RawConfigParser(allow_no_value=True)
dirPath = os.path.dirname(os.path.realpath(__file__))
configFilePath = os.path.join(dirPath, "config.ini")
print "configFilePath", configFilePath
with open(configFilePath) as f:
    user_config = f.read()
config.readfp(io.BytesIO(user_config))

# dmc section
DMC_INSTALL_PATH = config.get('dmc', 'INSTALL_PATH')
DMC_API_URI = config.get('dmc', 'API_URI')
DMC_IP = config.get('dmc', 'SERVER_HOST')
DMC_PORT = config.getint('dmc', 'SERVER_PORT')

# cmd section
ADB_COMMAND = config.get('cmd', 'ADB')
APPIUM_COMMAND = config.get('cmd', 'APPIUM')

# appium section
APPIUM_PORT = config.getint('appium', 'APPIUM_PORT')
APPIUM_BP_PORT = config.getint('appium', 'APPIUM_BP_PORT')

# computer section
COM_USER_NAME = config.get('computer', 'COM_USER_NAME')
COM_USER_PASS = config.get('computer', 'COM_USER_PASS')
COM_NODE_ID = config.get('computer', 'COM_NODE_ID')

# for device status in device dict
DEVICE_IS_IDLE = {'value': 1, 'label': 'idle'}
DEVICE_IS_BUSY = {'value': 2, 'label': 'busy'}

# additional data from server side, added up with device from scan
SERVER_DEVICE_TEMPLATE = {
            "status": DEVICE_IS_IDLE,
            "node": {
                "status": {
                    "value": 1,
                    "label": "up"
                },
                "cast": "http://127.0.0.1:7000",  # currently not in use
                "host": DMC_IP,		
                "id": COM_NODE_ID,
                "uri": "/api/v1/nodes/%s/" % COM_NODE_ID,  # append node-id
                "admin": COM_USER_NAME,
                "password": COM_USER_PASS,
                "detail": "{\"node\": \"localhost\"}",
                "type": "",  # client or server
            },
            "cast": "",
            "is_active": True,
            "is_removed": False,
            "id": "id-example",
            "uri": "/api/v1/devices/",  # append device-id
            "port": {
                "vstream_port": 7001,
                "wda_port": 8101,
                "appium_bp_port": 2742,
                "appium_port": 4724
            },
            "create_time": "",
        }


def cast_url_string(device):
    pixel = device["model"]["pixel"].split('x')
    return json.dumps(dict(
        name='common',
        host=DMC_IP,
        port=DMC_PORT,
        query=dict(
            udid=device["udid"],
            platform=device["model"]["platform"],
            width=pixel[0], height=pixel[1],
            forwardPort=SERVER_DEVICE_TEMPLATE["port"]["vstream_port"],
        )
    ))
