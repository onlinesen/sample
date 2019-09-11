#!/usr/bin/env python
# coding=utf8
from modules import utils
from modules import command
from modules.logs import Logs


def _display_adb_error(result):
    if result is not None and (result.startswith('adb: error:') or result.startswith('error:')):
        Logs.instance().error(result.strip())
        return True
    return False


def list_devices(details=False):
    args = ["devices"]
    if details:
        args.append("-l")
    result = command.execute("adb", args)
    _display_adb_error(result)

    lines = result.split("\n")
    devices = []
    for line in lines:
        if "List" not in line and ("device" in line or "offline" in line):
            data = line.split("\t")
            identifier = data[0].strip()
            identifier = identifier.rstrip("\r\n")
            device = {"identifier": identifier}
            devices.append(device)
    return devices


devices_list = [{'identifier': utils.get_option_value('--device', None)}] if utils.has_option('--device') else list_devices()

if devices_list:
    device_serial = ["-s", devices_list[0]['identifier']]


def shell(cmd):
    data = cmd.split()
    if data[0] != "shell":
        data.insert(0, "shell")

    result = command.execute("adb", device_serial + data)
    _display_adb_error(result)
    return result


def data_mode(close=True):
    if close:
        shell("svc data disable")
    else:
        shell("svc data enable")


def wifi_mode(close=True):
    if close:
        shell("svc wifi disable")
    else:
        shell("svc wifi enable")


def nfc_mode(close=True):
    if close:
        shell("svc nfc disable")
    else:
        shell("svc nfc enable")


def list_packages():
    result = shell("pm list packages")
    _display_adb_error(result)
    lines = result.split("\n")

    packages = []
    for line in lines:
        return


