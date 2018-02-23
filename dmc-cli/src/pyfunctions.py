# -*- coding: UTF-8 -*-
import logging
import os
import time
import subprocess
import shlex
import re
import settings
from settings import ADB_COMMAND, APPIUM_COMMAND


def download_file(remote_path):
    local_file = os.path.join(settings.DMC_INSTALL_PATH, remote_path.replace('/', '\\').strip('\\'))
    if os.path.isfile(local_file):
        print "processed local_file", local_file
        return local_file
    else:
        return ''


def mk_dirs(path):
    local_file_path = os.path.join(settings.DMC_INSTALL_PATH, path.replace('/', '\\').strip('\\'))
    if not os.path.isdir(local_file_path):
        logging.info('make-dirs: %s', local_file_path)
        os.makedirs(local_file_path)
    else:
        logging.info('dirs already exists: %s', local_file_path)
    return


def push_file(udid, local_file_path):  # default tmp folder on linux or mac
    # local_file_path = os.path.expanduser(local_file_path)
    if isinstance(local_file_path, unicode):
        local_file_path = local_file_path.encode('utf-8')
    _, name = os.path.split(local_file_path)
    local_file_path = local_file_path.replace('/', '\\').strip('\\')
    local_file_path = os.path.join(settings.DMC_INSTALL_PATH, local_file_path)
    storage_file_path = os.path.join('/data/local/tmp', name).replace('\\', '/')
    cmd = ADB_COMMAND + ' -s %(udid)s push %(local_file_path)s %(storage_file_path)s' \
                        % dict(udid=udid, local_file_path=local_file_path,
                               storage_file_path=storage_file_path)
    logging.info('push file: %s', cmd)
    subprocess.call(cmd)
    return storage_file_path


def stop_app(udid, package_name):
    cmd = ADB_COMMAND + ' -s %(udid)s shell am force-stop %(package)s' \
                        % dict(udid=udid, package=package_name)
    logging.info('stop_app: %s', cmd)
    return subprocess.call(cmd)


def uninstall_app(udid, package_name):
    cmd = ADB_COMMAND + ' -s %(udid)s shell pm uninstall %(package)s' \
                        % dict(udid=udid, package=package_name)
    logging.info('uninstall_app: %s', cmd)
    return subprocess.call(cmd)


def install_app(udid, apk_path, backend):
    if not backend:
        cmd = ADB_COMMAND + ' -s %(udid)s shell pm install -r %(apk)s' % dict(udid=udid, apk=apk_path)
        logging.info('install_app: %s', cmd)
        subprocess.call(cmd)
    else:
        cmd = "adb -s %(udid)s shell pm install -r '%(apk)s'" % dict(udid=udid, apk=apk_path)
        logging.info('install_app in backend: %s', cmd)
        args = shlex.split(cmd)
        args[0] = ADB_COMMAND
        subprocess.Popen(args, shell=True)


def launch_app(udid, package_name):
    cmd = ADB_COMMAND + ' -s %(udid)s shell am start -n %(package_name)s' % dict(udid=udid, package_name=package_name)
    logging.info('launch_app: %s', cmd)
    subprocess.call(cmd)


def change_appium_ime(udid):
    cmd = ADB_COMMAND + ' -s %(udid)s shell ime enable io.appium.android.ime/.UnicodeIM' % dict(udid=udid)
    logging.info('enable ime: %s', cmd)
    subprocess.call(cmd)
    cmd = ADB_COMMAND + ' -s %(udid)s shell ime set io.appium.android.ime/.UnicodeIME' % dict(udid=udid)
    logging.info('set ime: %s', cmd)
    subprocess.call(cmd)


def clear_user_data(udid, package_name):
    cmd = ADB_COMMAND + ' -s %(udid)s shell pm clear %(package_name)s' \
                        % dict(udid=udid, package_package_name=package_name)
    logging.info('clear user data: %s', cmd)
    subprocess.call(cmd)


def remove_file(udid, file_path):
    if isinstance(file_path, unicode):
        file_path = file_path.encode('utf-8')
    cmd = ADB_COMMAND + ' -s %(udid)s shell rm -rf %(file_path)s' \
                        % dict(udid=udid, file_path=file_path)
    logging.info('remove_file: %s', cmd)
    return subprocess.call(cmd)


def grant_permissions(udid, package_name):
    udid = udid.encode('utf-8')
    package_name = package_name.encode('utf-8')
    logging.info('grant_permissions for package %s', package_name)
    output = subprocess.check_output(
        ADB_COMMAND + " -s %(udid)s shell dumpsys package %(package_name)s | grep android.permission"
        % dict(udid=udid, package_name=package_name))
    # split into single element and clear whitespace on both sides
    permissions = [i.strip(' ') for i in output.split('\r\r\n') if i]
    # currently found delimiters = [',', ':']
    permissions = [re.split(r',+|:+', i, maxsplit=1).pop(0) for i in permissions]
    # remove duplicates
    permissions = list(set(permissions))
    for permission in permissions:
        subprocess.call(
            ADB_COMMAND + ' -s %(udid)s shell pm grant %(package_name)s %(android_permission)s'
            % dict(udid=udid, package_name=package_name, android_permission=permission))


# download apk from proxy to local machine
def put_file(app_path, apk):
    print "app_path", app_path
    name = app_path[str(app_path).rindex('/') + 1:]
    app_path = app_path.replace('/', '\\')
    app_dir = os.path.dirname(app_path)
    print "app_dir", app_dir
    local_dir = os.path.join(settings.DMC_INSTALL_PATH, app_dir.strip('\\'))
    print "local_dir", local_dir
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    local_path = os.path.join(local_dir, name)
    logging.info('put file to %s', local_path)
    apk.save(local_path)


def start_appium_server(port, bp_port, appium_log_path='', debug='false', kill_exist='false'):
    logging.info("start appium server at port %s and bp_port %s", port, bp_port)
    print "raw appium path", appium_log_path
    if appium_log_path != '':
        # path from task, client send '' as default
        appium_log_path = appium_log_path.replace('/', '\\').strip('\\')
        appium_log_path = os.path.join(settings.DMC_INSTALL_PATH, appium_log_path)
        appium_log_dir = os.path.dirname(appium_log_path)
        if not os.path.isdir(appium_log_dir):
            os.makedirs(appium_log_dir)
    print "processed appium path", appium_log_path
    # kill process with port
    if kill_exist == 'true':
        output = subprocess.check_output('netstat -a -n -o')
        lines = [line for line in output.split('\r\n') if line]
    	#delete the first two lines which may contain Chinese characters
    	lines = lines[2:]
        # get lines with port number
        tlines = [s for s in lines if port in s]
        # filter target_port into a list
        tpids = [filter(None, line.split(' ')).pop() for line in tlines]
        print tpids
        for tpid in tpids:
            if tpid != '0':
                os.system(r'taskkill /PID %s /F' % tpid)

    # start appium server with this port 
    cmd = ("appium --log-level %(log_level)s -lt 18000 --command-timeout 7200 --session-override "
           "-p %(port)s -bp %(bp_port)s --tmp 'C:\\Windows\\Temp\\%(bp_port)s' >> '%(appium_log_path)s'") \
          % dict(port=port, bp_port=bp_port, log_level='debug' if debug == 'true' else 'info',
                 appium_log_path=appium_log_path or os.path.join(settings.DMC_INSTALL_PATH,
                                                                 'appium_p{0}.log'.format(port)))
    args = shlex.split(cmd)
    args[0] = APPIUM_COMMAND
    time.sleep(1)  # wait for appium process to exit
    subprocess.Popen(args, shell=True)


def stop_appium_server(port):
    logging.info("stop appium server at port %s", port)
    output = subprocess.check_output('netstat -a -n -o')
    lines = [line for line in output.split('\r\n') if line]
    #delete the first two lines which may contain Chinese characters
    lines = lines[2:]
    # get lines with port number
    tlines = [s for s in lines if port in s]
    # filter target_port into a list
    tpids = [filter(None, line.split(' ')).pop() for line in tlines]
    for tpid in tpids:
        if tpid != '0':
            os.system(r'taskkill /PID %s /F' % tpid)
