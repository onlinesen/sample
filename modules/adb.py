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


def get_prop(property_name, default_value=None):
    result = shell("getprop" + property_name)
    _display_adb_error(result)

    if result is None or result.strip() == '':
        return default_value
    return result.strip()


def get_fingerprint():
    return get_prop('ro.build.fingerprint')


def get_product_model():
    return get_prop('ro.product.model')


def get_product_name():
    return get_prop('ro.product.name')


def get_software_info():
    board = get_prop('ro.board.platform')
    software = {
        'fingerprint': get_fingerprint(),
        'version_sdk': get_prop('ro.build.version.sdk'),
        'security_patch': get_prop('ro.build.version.security_patch'),
        'custom_build_version': get_prop('ro.custom.build.version'),
        'device': get_prop('ro.product.device'),
        'brand': get_prop('ro.product.brand'),
        'cpu_abi': get_prop('ro.product.cpu.abi'),
        'manufacturer': get_prop('ro.product.manufacturer'),
        'model': get_product_model(),
        'name': get_product_name(),
        'product': get_prop('ro.build.product'),
        'version_release': get_prop('ro.build.version.release'),
        'version_incremental': get_prop('ro.build.version.incremental'),
        'id': get_prop('ro.build.id'),
        'type': get_prop('ro.build.type'),
        'tags': get_prop('ro.build.tags'),
        'internal_build_version': get_prop('ro.internal.build.version'),
       # 'client_ids': get_client_ids(),
        'board': board,
        'vendor': utils.get_soc_from_board(board),
       # 'go_edition': is_go_edition(),
       # 'marketing_name': get_marketing_name()
    }
    return software


def get_hardware_info():
    hardware = {
        'hardware': get_prop('ro.hardware')
    }
    return hardware


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


