# -*- coding: UTF-8 -*-
import logging
import werkzeug
import time
import uuid
import copy
import settings
import pyfunctions
from flask import Flask, request, send_file
from flask_restful import reqparse, abort, Api, Resource
from flask_twisted import Twisted


app = Flask(__name__)
api = Api(app, prefix='/api/v1')


# enable Access-Control-Allow-Origin in header
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

logging.basicConfig(
    format="[dmcserver %(asctime)s] %(levelname)s %(message)s",
    level=logging.WARN)

'''global device dict for all APIs'''


devices = {}  # {device_id(udid): device_dict}
uuid2udid = {}  # {uuid: udid}

'''
API for local agent
'''


class Reset(Resource):
    @staticmethod
    def get():
        logging.info('signal RESET from client')
        global devices, uuid2udid
        devices.clear()
        uuid2udid.clear()
        return


class UpdateListFromAgentAPI(Resource):
    def __init__(self):
        super(UpdateListFromAgentAPI, self).__init__()
        self.appium_port = settings.APPIUM_PORT
        self.appium_bp_port = settings.APPIUM_BP_PORT

    def post(self):
        latest = request.get_json().get('latest')

        global devices, uuid2udid
        for device in devices.values():
            device['is_removed'] = True
        for device in latest:
            udid = device['udid']
            if udid not in devices:
                device_id = str(uuid.uuid4())
                devices[udid] = self.create_new_device(device_id, device)
                uuid2udid[device_id] = udid
            devices[udid]['is_removed'] = False
            devices[udid].update(device)
        return

    def create_new_device(self, device_id, scandevice):
        # create uuid and assign appium port for new device
        device = copy.deepcopy(settings.SERVER_DEVICE_TEMPLATE)
        create_time = time.strftime("%a, %d %b %Y %H:%M:%S -0000", time.localtime())
        device['id'] = device_id
        device['uri'] += device_id
        device['create_time'] = create_time
        device['port']['appium_port'] = self.appium_port
        device['port']['appium_bp_port'] = self.appium_bp_port
        device['node']['type'] = 'client'
        device['cast'] = settings.cast_url_string(scandevice)
        self.appium_port += 1
        self.appium_bp_port += 1
        return device


'''
API for master
'''


class DeviceListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('top')
        self.reqparse.add_argument('is_removed')
        self.reqparse.add_argument('datetime')
        self.reqparse.add_argument('platform')

    def get(self):
	args = self.reqparse.parse_args()
	platform = args.get('platform', '2')
	devices_list = copy.deepcopy(devices)
	if platform == '1':
            devices_list.clear()
	return {'devices': devices_list.values()}


class DeviceAPI(Resource):
    def __init__(self):
        super(DeviceAPI, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name')
        self.reqparse.add_argument('is_removed', type=bool)

    @staticmethod
    def get(id):
        # return device of the id in args
        device = devices.get(uuid2udid.get(id))
        if device:
            return device
        else:
            abort(404, error='device %s not found' % id)

    @staticmethod
    def patch(self, id):
        # set if device if removed or not
        global devices
        device = devices.get(uuid2udid.get(id))
        if device:
            args = self.reqparse.parse_args()
            name = args.get('name')
            is_removed = args.get('is_removed')
            device = devices[id]
            device['name'] = name or device['name']
            device['is_removed'] = is_removed
        else:
            abort(404, error='device %s not found' % id)
        return {}


class DeviceUseAPI(Resource):
    @staticmethod
    def patch(id):
        global devices
        device = devices.get(uuid2udid.get(id))
        if device:
            if device['is_removed']:
                abort(500, error='device is already removed')
            elif device['status'] != settings.DEVICE_IS_IDLE:
                abort(500, error='device is already in use')
            else:
                device['status'] = settings.DEVICE_IS_BUSY
        else:
            abort(404, error='device %s not found' % id)
        return {}


class DeviceFreeAPI(Resource):
    @staticmethod
    def patch(id):
        global devices
        device = devices.get(uuid2udid.get(id))
        if device:
            if device['status'] == settings.DEVICE_IS_BUSY:
                device['status'] = settings.DEVICE_IS_IDLE
        else:
            abort(404, error='device %s not found' % id)
        return {}


'''
API for proxy remote control
'''


class DownloadFileApi(Resource):
    def __init__(self):
        super(DownloadFileApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('remote_path')
        self.reqparse.add_argument('local_path')

    def get(self):
        args = self.reqparse.parse_args()
        remote_path = args.get('remote_path')
        local_file = pyfunctions.download_file(remote_path)
        if local_file:
            return send_file(local_file)
        else:
            abort(404, error='file %s not found' % remote_path)


class MakeDirsApi(Resource):
    def __init__(self):
        super(MakeDirsApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('path')

    def patch(self):
        args = self.reqparse.parse_args()
        path = args.get('path')
        pyfunctions.mk_dirs(path)
        return


class InstallAppApi(Resource):
    def __init__(self):
        super(InstallAppApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('app_path')
        self.reqparse.add_argument('package_name')
        self.reqparse.add_argument('backend', type=bool)

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        app_path = args.get('app_path')
        package_name = args.get('package_name')
        backend = args.get('backend')
        apk_path = pyfunctions.push_file(udid, app_path)
        pyfunctions.stop_app(udid, package_name)
        pyfunctions.uninstall_app(udid, package_name)
        pyfunctions.install_app(udid, apk_path, backend)
        # pyfunctions.remove_file(udid, apk_path)
        return


class UninstallAppApi(Resource):
    def __init__(self):
        super(UninstallAppApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('package_name')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        package_name = args.get('package_name')
        pyfunctions.uninstall_app(udid, package_name)
        return


class LaunchAppApi(Resource):
    def __init__(self):
        super(LaunchAppApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('package_name')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        package_name = args.get('package_name')
        pyfunctions.launch_app(udid, package_name)
        return


class StopAppApi(Resource):
    def __init__(self):
        super(StopAppApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('package_name')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        package_name = args.get('package_name')
        pyfunctions.stop_app(udid, package_name)
        return


class RemoveFileApi(Resource):
    def __init__(self):
        super(RemoveFileApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('file_path')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        file_path = args.get('file_path')
        pyfunctions.remove_file(udid, file_path)
        return


class GrantPermissionsApi(Resource):
    def __init__(self):
        super(GrantPermissionsApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('package_name')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        package_name = args.get('package_name')
        pyfunctions.grant_permissions(udid, package_name)
        return


class ChangeAppiumImeApi(Resource):
    def __init__(self):
        super(ChangeAppiumImeApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        pyfunctions.change_appium_ime(udid)
        return


class ClearUserDataApi(Resource):
    def __init__(self):
        super(ClearUserDataApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('udid')
        self.reqparse.add_argument('package_name')

    def patch(self):
        args = self.reqparse.parse_args()
        udid = args.get('udid')
        package_name = args.get('package_name')
        pyfunctions.clear_user_data(udid, package_name)
        return


class PutFileApi(Resource):
    def __init__(self):
        super(PutFileApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('app_path')
        self.reqparse.add_argument('apk', type=werkzeug.datastructures.FileStorage, location='files')

    def post(self):
        args = self.reqparse.parse_args()
        app_path = args.get('app_path')
        apk = args.get('apk')
        pyfunctions.put_file(app_path, apk)
        return


class StartAppiumServerApi(Resource):
    def __init__(self):
        super(StartAppiumServerApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('port')
        self.reqparse.add_argument('bp_port')
        self.reqparse.add_argument('appium_log_path')

    def patch(self):
        args = self.reqparse.parse_args()
        port = args.get('port')
        bp_port = args.get('bp_port')
        appium_log_path = args.get('appium_log_path')
        debug = args.get('debug')
        kill_exist = args.get('kill_exist')
        pyfunctions.start_appium_server(port, bp_port, appium_log_path, debug, kill_exist)
        return


class StopAppiumServerApi(Resource):
    def __init__(self):
        super(StopAppiumServerApi, self).__init__()
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('port')

    def patch(self):
        args = self.reqparse.parse_args()
        port = args.get('port')
        pyfunctions.stop_appium_server(port)
        return


# api for agent
api.add_resource(Reset, '/reset')
api.add_resource(UpdateListFromAgentAPI, '/update')

# api for master
api.add_resource(DeviceListAPI, '/devices')

# api for proxy device usage
api.add_resource(DeviceAPI, '/devices/<string:id>')
api.add_resource(DeviceUseAPI, '/devices/<string:id>/use')
api.add_resource(DeviceFreeAPI, '/devices/<string:id>/free')

# api for proxy commands
api.add_resource(DownloadFileApi, '/download-file')
api.add_resource(MakeDirsApi, '/mk-dirs')
api.add_resource(InstallAppApi, '/install-app')
api.add_resource(UninstallAppApi, '/uninstall-app')
api.add_resource(LaunchAppApi, '/launch-app')
api.add_resource(StopAppApi, '/stop-app')
api.add_resource(RemoveFileApi, '/remove-file')
api.add_resource(GrantPermissionsApi, '/grant-permissions')
api.add_resource(ChangeAppiumImeApi, '/change-appium-ime')
api.add_resource(ClearUserDataApi, '/clear-user-data')
api.add_resource(PutFileApi, '/put-file')
api.add_resource(StartAppiumServerApi, '/start-appium-server')
api.add_resource(StopAppiumServerApi, '/stop-appium-server')


twisted = Twisted(app)
if __name__ == '__main__':
    # only for debug use
    twisted.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(host='0.0.0.0', port=5000, threaded=True)
