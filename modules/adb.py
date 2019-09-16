#!/usr/bin/env python
# coding=utf8
import os
import time

from modules import android_users
#from modules import apktool
from modules import command
from modules import files
#from modules import report
from modules import strings
from modules import utils
from modules.logs import Logs

APKSIGNER_ENABLED = False

KEY_CLIENT_ID_BASE = 'client_id_base'
KEY_CLIENT_ID = "client_id"
KEY_SEARCH_CLIENT_ID = "search_client_id"
KEY_CHROME_CLIENT_ID = "chrome_client_id"
KEY_MAPS_CLIENT_ID = "maps_client_id"
KEY_YOUTUBE_CLIENT_ID = "youtube_client_id"
KEY_MARKET_CLIENT_ID = "market_client_id"
KEY_WALLET_CLIENT_ID = "wallet_client_id"

_ISSUE_TYPE = "GET_APK"

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
            identifier = identifier.rstrip('\r\n')
            device = {'identifier': identifier}
            devices.append(device)

    return devices


devices_list = [{'identifier': utils.get_option_value('--device', None)}] if utils.has_option('--device') else list_devices()

if devices_list:
    device_serial = ["-s", devices_list[0]['identifier']]


def _get_build_tools_version_path(root_path):
    if utils.is_platform_windows():
        build_tools_path = files.path_combine(root_path, 'libs', 'android', 'windows', 'build-tools') + os.sep
    elif utils.is_platform_mac():
        build_tools_path = files.path_combine(root_path, 'libs', 'android', 'mac', 'build-tools') + os.sep
    else:
        build_tools_path = files.path_combine(root_path, 'libs', 'android', 'linux', 'build-tools') + os.sep

    sub_folders = files.list_files(build_tools_path)

    build_tools_version = None
    for sub_folder in sub_folders:
        build_tools_version = files.path_combine(build_tools_path, sub_folder)
        break

    return build_tools_version


def _get_aapt_path(root_path):
    build_tools_version = _get_build_tools_version_path(root_path)
    if build_tools_version is None:
        return None

    aapt_path = files.path_combine(build_tools_version, 'aapt')
    return aapt_path


def _get_apk_signer_path(root_path):
    build_tools_version = _get_build_tools_version_path(root_path)
    if build_tools_version is None:
        return None

    apk_signer_path = files.path_combine(build_tools_version, 'apksigner')
    return apk_signer_path


def list_packages(root_path, package_pattern=None, last_version=False):
    """
    list packages [-f] [-d] [-e] [-s] [-3] [-i] [-u] [--user USER_ID] [FILTER]
    Prints all packages; optionally only those whose name contains
    the text in FILTER.
    Options:
      -f: see their associated file
      -d: filter to only show disabled packages
      -e: filter to only show enabled packages
      -s: filter to only show system packages
      -3: filter to only show third party packages
      -i: see the installer for the packages
      -u: also include uninstalled packages
    """
    result = shell("pm list packages -f")
    _display_adb_error(result)

   # users = android_users.get_android_users_list(root_path)
    users = 1

    lines = result.split("\n")

    packages = []
    for line in lines:
        if line:
            name = strings.extract_regex_value(line, '(?:=([a-zA-Z0-9\\-\\._ ]{3,}))')
            path = line.replace(name, '').replace('package:', '').replace('.apk=', '.apk').strip()

            if (package_pattern is None) or utils.is_matching_package(name, package_pattern):

                # Determine if it's system app:
                system = (
                        '/vendor/app/' in path or
                        '/system/priv-app/' in path or
                        '/system/app/' in path
                )

                Logs.instance().info('\tDumping package info: ' + name)
                info = _get_package_info(name, path, system, users, last_version)
                # Logs.instance().info('\tDone !\n')

                if info is not None:
                    p = {'name': name, 'path': path, 'system': system}
                    package = utils.merge_dicts(p, info)
                    packages.append(package)

    # exit()
    return packages


def list_files_pattern(pattern, path='.', output_file=None):
    # adb shell "find . -name '*.sh'" > output-scripts.txt
    find_cmd = "find " + path + " -name '" + pattern + "'"

    args = device_serial + ["shell", find_cmd]

    if output_file is not None:
        args.append(">")
        args.append(output_file)

    result = command.execute("adb", args, False)
    _display_adb_error(result)

    lines = result.split()
    filtered_lines = []
    for line in lines:
        if not line.endswith("Permission denied"):
            filtered_lines.append(line)
    return filtered_lines


def list_files_extension(file_extension, path='.', output_file=None):
    # adb shell "find . -name '*.sh'" > output-scripts.txt
    find_cmd = "find " + path + " -name '*." + file_extension + "'"

    args = device_serial + ["shell", find_cmd]

    if output_file is not None:
        args.append(">")
        args.append(output_file)

    result = command.execute("adb", args, False, False, True)
    _display_adb_error(result)

    lines = result.split("\n")
    filtered_lines = []
    for line in lines:
        clean_line = line.strip()
        if not clean_line.endswith("Permission denied") and clean_line.endswith(file_extension):
            filtered_lines.append(clean_line)
    return filtered_lines


def get_custom_build_version():
    soft_version = get_prop('ro.custom.build.version')
    if soft_version is None or soft_version == '':
        soft_version = get_fingerprint()
    return soft_version


def get_fingerprint():
    return get_prop('ro.build.fingerprint')


def get_product_model():
    return get_prop('ro.product.model')


def get_product_name():
    return get_prop('ro.product.name')


def get_marketing_name():
    # Wiko
    name = get_prop('ro.product.market')
    # Google Pixel
    if strings.is_empty(name):
        name = get_prop('ro.product.vendor.model')
    # HUAWEI
    if strings.is_empty(name):
        name = get_prop('ro.config.marketing_name')
    # AOSP
    if strings.is_empty(name):
        name = get_prop('ro.product.name')
    return name


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
        'client_ids': get_client_ids(),
        'board': board,
        'vendor': utils.get_soc_from_board(board),
        'go_edition': is_go_edition(),
        'marketing_name': get_marketing_name()
    }
    return software


def is_go_edition():
    version_sdk = int(get_prop('ro.build.version.sdk'))
    if version_sdk >= 27:  # >= Android 8.1
        low_ram = get_prop('ro.config.low_ram')
        lmk_critical_upgrade = get_prop('ro.lmk.critical_upgrade')
        lmk_upgrade_pressure = int(get_prop('ro.lmk.upgrade_pressure', 0))
        return utils.to_boolean(low_ram) and utils.to_boolean(lmk_critical_upgrade) and lmk_upgrade_pressure == 40
    return False


def _get_content_partner():
    # adb shell content query --uri content://com.google.settings/partner
    result = shell("content query --uri content://com.google.settings/partner")
    _display_adb_error(result)
    return result.strip().split("\n")


def shell(cmd):
    data = cmd.split()
    if data[0] != "shell":
        data.insert(0, "shell")

    result = command.execute("adb", device_serial + data)
    _display_adb_error(result)
    return result


def get_prop(property_name, default_value=None):
    result = shell("getprop " + property_name)
    _display_adb_error(result)

    if result is None or result.strip() == '':
        return default_value

    return result.strip()


def get_all_prop():
    result = shell("getprop")
    _display_adb_error(result)

    lines = result.split("\n")
    props = []

    for line in lines:
        if line.startswith("["):
            data = line.split(']:')
            name = data[0].replace('[', '')
            value = data[1].replace('[', '').replace(']', '')
            props.append({'name': name, 'value': value})

    return props


def pull(source, destination, ignore_error_no_file=False):
    result = command.execute("adb", device_serial + ["pull", source, destination])
    if not ignore_error_no_file or \
            (not strings.str_contains(result, "No such file or directory")
             and not strings.str_contains(result, "does not exist")):
        _display_adb_error(result)
    return result


def alternative_pull(source, destination):
    result = cat_file(source)

    if result.startswith("cat: " + source):
        result = "error: " + result
        _display_adb_error(result)
        return result

    if utils.is_platform_windows():
        result = strings.r_replace(result, "\x0D\x0A", "\x0A")

    files.write_binary_file(destination, result)

    if files.file_exists(destination):
        return "Alternative pull successful"

    return "error: Could not create file " + destination



def push(source, destination):
    result = command.execute("adb", device_serial + ["push", source, destination])
    _display_adb_error(result)
    return result


def is_installed(pkg):
    result = shell("pm path " + pkg)
    _display_adb_error(result)
    return result.startswith("package:")


def install(apk_file_path, option_replace=True, option_test=False, option_grant=False):
    args = device_serial + ["install"]
    if option_replace:
        args.append("-r")
    if option_test:
        args.append("-t")
    if option_grant:
        args.append("-g")
    args.append(apk_file_path)
    result = command.execute("adb", args, False)
    _display_adb_error(result)
    return result.strip()


def uninstall(package_name, keep_user_data=False):
    args = device_serial + ["uninstall"]
    if keep_user_data:
        args.append("-k")
    args.append(package_name)
    result = command.execute("adb", args, False)
    _display_adb_error(result)
    return result.strip()


def start_activity(package_name, activity_name=None):
    # adb shell am start com.package.name/.MainActivity
    args = device_serial + ["shell", "am", "start"]
    if activity_name is not None:
        args.append(package_name + "/" + activity_name)
    else:
        args.append(package_name)
    result = command.execute("adb", args, False)
    _display_adb_error(result)
    return result.strip()


def resolve_user(users, user_id):
    if users is None or user_id is None:
        return None

    # https://android.googlesource.com/platform/system/core/+/master/libcutils/include/private/android_filesystem_config.h

    if 10000 <= user_id <= 19999:
        return {'value': user_id, 'tag': 'AID_APP', 'description': 'App user'}

    if 20000 <= user_id <= 29999:
        return {'value': user_id, 'tag': 'AID_CACHE_GID', 'description': 'Cache GID'}

    if 30000 <= user_id <= 39999:
        return {'value': user_id, 'tag': 'AID_EXT_GID', 'description': 'Ext GID'}

    if 40000 <= user_id <= 49999:
        return {'value': user_id, 'tag': 'AID_EXT_CACHE_GID', 'description': 'Ext Cache GID'}

    if 50000 <= user_id <= 59999:
        return {'value': user_id, 'tag': 'AID_SHARED_GID', 'description': 'Shared GID'}

    if 99000 <= user_id <= 99999:
        return {'value': user_id, 'tag': 'AID_ISOLATED', 'description': 'Isolated'}

    for user in users:
        if int(user['value']) == int(user_id):
            return user

    return None


def _apk_is_multidex(root_path, apk_path):
    aapt_path = _get_aapt_path(root_path)
    result = command.execute(aapt_path, ["list", apk_path])
    _display_adb_error(result)

    if result is None:
        return False

    lines = result.split()
    counter = 0

    for line in lines:
        if line.endswith('.dex'):
            counter += 1

    return counter > 1


def get_apk_info(root_path, apk_path):
    aapt_path = _get_aapt_path(root_path)
    result = command.execute(aapt_path, ["dump", "badging", apk_path])
    _display_adb_error(result)

    info = _get_default_package_info()
    info['name'] = strings.extract_regex_value(result, r"(?:package:\s*name='([a-zA-Z0-9\.\_\-]*)')")
    info['path'] = apk_path

    users = android_users.get_android_users_list(root_path)
    info['user'] = resolve_user(users, info['user_id'])

    info['version_code'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:versionCode='([0-9]*)')"))
    info['version_name'] = strings.extract_regex_value(result, r"(?:versionName='([\s0-9a-zA-Z\-\(\)\.\_\[\]]{1,})')")

    info['min_sdk'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:sdkVersion:'([0-9]{1,})')"))
    info['target_sdk'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:targetSdkVersion:'([0-9]{1,})')"))

    info['multidex'] = _apk_is_multidex(root_path, apk_path)
   # info['signature'] = get_signature_info(root_path, apk_path)

    return info


def _get_package_info(package_name, package_path, system, users, latest_version):
    result = shell("dumpsys package " + package_name)
    _display_adb_error(result)

    index = result.find("Hidden system packages:")
    if latest_version and index > -1:
        result = result[:index]
    if not latest_version and index > -1:
        result = result[index:]

    if result is None or strings.contains_regex(result, 'Unable to find'):
        Logs.instance().warning('Dumpsys failed for package: ' + package_name)
        return None

    flag = False
    info = _get_default_package_info()
    info['manifest'] = None

    info['name'] = package_name
    info['path'] = package_path
    info['system'] = system

    info['user_id'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:userId=([0-9]*))", flag))
    info['user'] = resolve_user(users, info['user_id'])

    info['version_code'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:versionCode=([0-9]*))", flag))
    info['version_name'] = strings.extract_regex_value(result, r"(?:versionName=([0-9a-zA-Z\-\(\)\.\_\[\]]*))", flag)

    info['min_sdk'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:minSdk=([0-9]*))", flag))
    info['target_sdk'] = utils.str_to_int(strings.extract_regex_value(result, r"(?:targetSdk=([0-9]*))", flag))

    flags = []
    pkg_lags = strings.extract_regex_value(result, r"(?:pkgFlags=\[([\sA-Z\_]*)\])", flag)
    if pkg_lags is not None:
        flags = pkg_lags.strip().split()

    for flag in flags:
        if flag == 'SYSTEM':
            info['system'] = True
        info['pkg_flags'].append(flag.strip())

    info['code_path'] = strings.extract_regex_value(result, r"(?:codePath=([0-9a-zA-Z\/\-\_\.=]+))", flag)
    info['odex'] = None

    # retro compatibility (Android 6)
    if info['odex'] is None and info['system']:
        items = list_files_extension('odex', info['code_path'])
        if len(items) > 0 and items[0].endswith('.odex'):
            info['odex'] = items[0]

    # Fix Package path (O MR1)
    if not package_path.startswith(info['code_path']):
        items = list_files_extension('apk', info['code_path'])
        if len(items) > 0 and items[0].endswith('.apk'):
            info['old_path'] = package_path
            info['path'] = items[0]
        else:
            info['old_path'] = package_path
            info['path'] = strings.extract_regex_value(result, r"(?:path:\s*([0-9a-zA-Z\/\-\_\=\.]+))", True)

    return info


def _get_default_package_info():
    info = {
        'label': None,
        # AID_APP_START
        'user_id': 10000,
        'user': None,
        'version_code': 0,
        'version_name': None,
        'version_min': None,
        'version_max': None,
        'min_sdk': 0,
        'target_sdk': 0,
        'pkg_flags': [],
        'system': False,
        'code_path': None,
        'odex': None,
        'path': None,
        'multidex': False,
        'signature': None,
        # Flag to decompile or not the APK:
        'decompile': True,
        'partition': None
    }

    return info





def has_feature(feature_name):
    # adb shell pm list features | grep -i com.google.android.feature.EEA_DEVICE
    result = shell("pm list features | grep -i " + feature_name)
    _display_adb_error(result)

    return (result is None) or (strings.contains_regex(result, feature_name))


def get_client_ids():
    result = {}

    # adb shell content query --uri content://com.google.settings/partner
    rows = _get_content_partner()

    """
    Row: 0 _id=28, name=use_location_for_services, value=1
    Row: 1 _id=532, name=data_store_version, value=3
    Row: 2 _id=533, name=client_id, value=android-wiko
    Row: 3 _id=534, name=search_client_id, value=ms-android-wiko
    Row: 4 _id=535, name=chrome_client_id, value=ms-android-wiko
    Row: 5 _id=536, name=maps_client_id, value=gmm-android-wiko
    Row: 6 _id=537, name=youtube_client_id, value=mvapp-android-wiko
    Row: 7 _id=538, name=market_client_id, value=am-android-wiko
    Row: 8 _id=539, name=network_location_opt_in, value=1
    """

    for row in rows:
        name = strings.extract_regex_value(row, r"(?:name=([a-z\_]{1,}))")
        value = strings.extract_regex_value(row, r"(?:value=([a-z0-9\_\-]{1,}))")
        if name == KEY_CLIENT_ID:
            result[name] = value
        elif name == KEY_SEARCH_CLIENT_ID:
            result[name] = value
        elif name == KEY_CHROME_CLIENT_ID:
            result[name] = value
        elif name == KEY_MAPS_CLIENT_ID:
            result[name] = value
        elif name == KEY_YOUTUBE_CLIENT_ID:
            result[name] = value
        elif name == KEY_MARKET_CLIENT_ID:
            result[name] = value
        elif name == KEY_WALLET_CLIENT_ID:
            result[name] = value

    # adb shell getprop ro.com.google.clientidbase
    result[KEY_CLIENT_ID_BASE] = get_prop('ro.com.google.clientidbase')

    return result


def device_awake_and_unlocked():
    # adb shell dumpsys power
    result = shell("dumpsys power | grep 'mHolding'")
    _display_adb_error(result)
    # Logs.instance().debug(result)

    #  mHoldingWakeLockSuspendBlocker=true
    wake_lock_suspend_blocker = utils.to_boolean(
        strings.extract_regex_value(result, r"(?:mHoldingWakeLockSuspendBlocker=([a-zA-Z]{4,5}))"))
    # Logs.instance().debug("mHoldingWakeLockSuspendBlocker = " + str(wake_lock_suspend_blocker))

    #  mHoldingDisplaySuspendBlocker=true
    display_suspend_blocker = utils.to_boolean(
        strings.extract_regex_value(result, r"(?:mHoldingDisplaySuspendBlocker=([a-zA-Z]{4,5}))"))
    # Logs.instance().debug("mHoldingDisplaySuspendBlocker = " + str(display_suspend_blocker))

    if not wake_lock_suspend_blocker and not display_suspend_blocker:
        Logs.instance().warning("Screen if not awake!")

    if not wake_lock_suspend_blocker and display_suspend_blocker:
        Logs.instance().warning("Screen awake but locked!")

    if wake_lock_suspend_blocker and display_suspend_blocker:
        Logs.instance().info("Screen awake and unlocked!")
        return True

    return False


def get_foreground_component(use_regex=True):
    # adb shell dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'
    result = shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
    _display_adb_error(result)
    if not use_regex:
        return result
    # Logs.instance().debug(result)

    regex = r"(?:u0\s([0-9a-zA-Z\.\/\-\_]{4,})\})"
    app = strings.extract_regex_value(result, regex)
    # Logs.instance().debug("Foreground app: " + str(app))
    return app


def display_launcher():
    # adb shell am start -c android.intent.category.HOME -a android.intent.action.MAIN
    shell("am start -c android.intent.category.HOME -a android.intent.action.MAIN")
    time.sleep(1)


def get_default_launcher():
    # Display Launcher:
    display_launcher()

    # Get Launcher Component
    launcher_component = get_foreground_component()
    if launcher_component is not None:
        # print(launcher_component)
        data = launcher_component.split("/")
        # print(data)
        if len(data) == 2:
            return {"package_name": data[0], "activity_name": data[1]}
    return None


def get_battery():
    result = shell("dumpsys battery")

    if _display_adb_error(result) or result is None:
        return None

    lines = result.split("\n")
    info = None

    for line in lines:
        if ': ' in line:
            if info is None:
                info = {}
            data = line.split(': ')
            key = data[0].strip().lower().replace(' ', '_')
            value = data[1].strip()
            info[key] = value

    return info


def get_cpu_info():
    result = shell("dumpsys cpuinfo")

    if _display_adb_error(result) or result is None:
        return None

    lines = result.split("\n")
    info = None

    dates = strings.extract_regex(result, r"([0-9]{4}-[0-9]{2}-[0-9]{2}\s+[0-9]{2}:[0-9]{2}:[0-9]{2})")
    if len(dates) < 2:
        return None

    date_from = dates[0]['match']
    date_to = dates[1]['match']

    for line in lines:

        if info is None:
            info = []

        ratio = strings.extract_regex_value(line, r"(?:^\s*([0-9\.]{1,6}%))")
        if ratio is not None:
            pid = strings.extract_regex_value(line, r"(?:\s([0-9]{1,8})\/)")
            package = strings.extract_regex_value(line, r"(?:[0-9]\/([a-zA-Z0-9\.\_\-\@\:\/]{1,}):\s)")
            ratio_user = strings.extract_regex_value(line, r"(?:\s([0-9\.%]{1,5})\suser\s)")
            ratio_kernel = strings.extract_regex_value(line, r"(?:\s([0-9\.%]{1,5})\skernel\s)")
            faults_minor = strings.extract_regex_value(line, r"(?:faults:\s([0-9]{1,8})\sminor)")
            faults_major = strings.extract_regex_value(line, r"(?:minor\s([0-9]{1,8})\smajor)")

            info.append({
                'date_from': date_from,
                'date_to': date_to,

                'time_from': utils.to_timestamp(date_from),
                'time_to': utils.to_timestamp(date_to),

                'ratio': ratio,
                'pid': utils.str_to_int(pid),
                'package': package,
                'ratio_user': ratio_user,
                'ratio_kernel': ratio_kernel,
                'faults_minor': utils.str_to_int(faults_minor),
                'faults_major': utils.str_to_int(faults_major)
            })

    return info


def get_memory_info():
    result = shell("dumpsys meminfo")

    if _display_adb_error(result) or result is None:
        return None

    lines = result.split("\n")
    info = None

    up_time = strings.extract_regex_value(result, r"(?:Uptime:\s([0-9]+)\s)")
    total_ram = strings.extract_regex_value(result, r"(?:Total RAM:\s+([0-9,]+)K)")
    free_ram = strings.extract_regex_value(result, r"(?:Free RAM:\s+([0-9,]+)K)")
    used_ram = strings.extract_regex_value(result, r"(?:Used RAM:\s+([0-9,]+)K)")
    lost_ram = strings.extract_regex_value(result, r"(?:Lost RAM:\s+([0-9,]+)K)")
    z_ram = strings.extract_regex_value(result, r"(?:ZRAM:\s+([0-9,]+)K)")
    status = strings.extract_regex_value(result, r"\(status\s+([a-zA-Z]+)\)")

    for line in lines:

        if info is None:
            info = []
        elif line.strip() == "Total PSS by OOM adjustment:":
            break

        mem_size = strings.extract_regex_value(line, r"(?:\s*([0-9,]+)K)")

        if mem_size is not None:
            process_name = strings.extract_regex_value(line, r"(?:\s*([a-zA-Z0-9\:\.\@\-\_/]+)\s*\()")
            process_id = strings.extract_regex_value(line, r"(?:\(pid\s*([0-9]+)\))")

            info.append({
                'up_time': utils.str_to_int(up_time),

                'total_ram': utils.str_to_int(strings.replace(total_ram, ",")),
                'free_ram': utils.str_to_int(strings.replace(free_ram, ",")),
                'used_ram': utils.str_to_int(strings.replace(used_ram, ",")),
                'lost_ram': utils.str_to_int(strings.replace(lost_ram, ",")),
                'z_ram': utils.str_to_int(strings.replace(z_ram, ",")),
                'status': status,

                'mem_size': utils.str_to_int(strings.replace(mem_size, ",")),
                'process_name': process_name,
                'process_id': utils.str_to_int(process_id)
            })

    return info


def get_network():
    result = shell("dumpsys netstats")

    if _display_adb_error(result) or result is None:
        return None

    lines = result.split("\n")
    if len(lines) < 2:
        return None

    line = lines[1]

    info = {
        'interface': strings.extract_regex_value(line, r"(?:iface=([a-z0-9_\-]+))"),
        'type': strings.extract_regex_value(line, r"(?:(?:\{|\s)type=([a-z0-9_\-]+))"),
        'sub_type': strings.extract_regex_value(line, r"(?:\ssubType=([a-z0-9_\-]+))"),
        'network_id': strings.extract_regex_value(line, r"(?:\snetworkId=([a-z0-9_\-]+))"),
        'metered': strings.extract_regex_value(line, r"(?:\smetered=([a-z0-9_\-]+))"),
        'subscriber_id': strings.extract_regex_value(line, r"(?:\ssubscriberId=([a-z0-9_\-\.]+))"),
        'default_network': strings.extract_regex_value(line, r"(?:\sdefaultNetwork=([a-z0-9_\-]+))"),
    }

    return info


def monkey(package_name=None, duration_seconds=30, throttle=1000, log_file=None):
    # https://developer.android.com/studio/test/monkey

    seed = 42
    ratio_bug_fix = 4
    event_count = int(duration_seconds * (1000 / throttle) * ratio_bug_fix)

    args = device_serial + ["shell", "monkey", "-v",
                            "-s", seed,  # Seed value for pseudo-random number generator
                            ]

    if package_name is not None:
        args = args + ["-p", package_name]

    args = args + ["--throttle", throttle,  # Inserts a fixed delay between events
                   "--ignore-crashes",
                   "--ignore-timeouts",  # Application Not Responding
                   "--ignore-security-exceptions",  # Permissions error
                   event_count,  # Event count
                   ">", log_file]

    result = command.execute("adb", args, no_wait=True, display_cmd=True)

    _display_adb_error(result)


def cat_file(file_path):
    return shell("cat " + file_path)


def file_exists(file_path):
    return shell('[ -f "{0}" ] && echo "1"'.format(file_path)).strip() == "1"


def get_whitelisted_apps():
    board = get_prop("ro.board.platform")
    soc = utils.get_soc_from_board(board)

    if soc == utils.SOC_MEDIATEK:
        return get_whitelisted_apps_mtk()

    if soc == utils.SOC_UNISOC:
        return get_whitelisted_apps_unisoc()

    return []


def get_whitelisted_apps_mtk():
    whitelists = ["/etc/permissions/pms_sysapp_removable_system_list.txt",
                  "/product/etc/permissions/pms_sysapp_removable_product_list.txt"]

    cat_result = ""

    for whitelist in whitelists:
        if file_exists(whitelist):
            cat_result += cat_file(whitelist)

    result = [x.strip() for x in cat_result.strip().split("\n")]

    return result

def get_packages_counts():
    apps = shell("pm list packages| wc -l").strip()
    return apps


def get_whitelisted_apps_unisoc():
    apps = shell("pm list packages -f | grep /preloadapp/")

    lines = apps.strip().split("\n")
    result = []

    for line in lines:
        if line:
            result.append(line.strip().split("=")[1])

    return result


def delete_file(path):
    result = command.execute("adb", ["shell", "rm", path]).strip()
    # Logs.instance().debug("Result delete = " + result)
    if result.find("rm: " + path + ":") > -1:
        Logs.instance().info("Couldn't remove file from device: " + result)


def screenshot(desc_file):
    try:
        shell("shell screencap -p sdcard/screen.png")
        result = pull("sdcard/screen.png", desc_file)
        Logs.instance().info("Result screenshot = " + result)
        return True if "1 file pulled" in result else False
    except:
        return False


def get_uiautomator_path():
    # Generate an XML file that describe the UI of the connected device
    result = shell('shell uiautomator dump')
    # Sometimes result is empty, please try to replug your device to your computer
    index_start = result.find('/')
    # Find path to the XML file on the device
    path_to_file = result[1 + index_start:].replace('\n', '').replace('\r', '')
    return path_to_file


def input_tap(x, y):
    shell("shell input tap " + str(x) + " " + str(y))


def input_text(text):
    shell("shell input text '" + text + "'")


def input_swipe(start_x, start_y, end_x, end_y, duration):
    shell("shell input swipe " +
          str(start_x) + " " + str(start_y) + " " + str(end_x) + " " + str(end_y) + " " + str(duration))


def input_keyevent(keyevent):
    shell("shell input keyevent " + str(keyevent))


def adb_reboot(unlock=True):
    command.execute("adb", device_serial + ["reboot"])
    time.sleep(20)
    wait_for_device()

    if unlock:
        unlock_device()

    device_status = get_state().strip()

    return device_status == "device"


def unlock_device():
    result = shell("dumpsys window policy |grep isStatusBarKeyguard")

    if "isStatusBarKeyguard=true" in result:
        w, h = get_wm_size()

        if not is_screen_on():
            shell("input keyevent 26")
            time.sleep(1)

        shell("input swipe {} {} {} {} {}".format(int(w) / 2, int(h) / 2, int(w), '100', '1000'))
        time.sleep(1)

    result = shell("dumpsys window policy |grep isStatusBarKeyguard")

    return "isStatusBarKeyguard=false" in result


def is_screen_on():
    result = shell("dumpsys window policy |grep ScreenOnEarly")
    return True if "mScreenOnEarly=true" in result else False


def get_wm_size():
    result = shell("wm size")
    w, h = strings.extract_regex_value(result, r"(\d{1,})", False), strings.extract_regex_value(result, r"(\d{1,})",
                                                                                                True)
    return w, h


def uiautomator_dump():
    for i in range(0, 30):
        result = shell("uiautomator dump")
        time.sleep(1.5)
        Logs.instance().info('\tUIAutomator dumping..' + '.' * i)

        if 'window_dump.xml' in result:
            result = cat_file("/sdcard/window_dump.xml")

            if "hierarchy" in result:
                return result


# return all apps in launcher
def get_apps_in_launcher():
    launcher_apps_list = []

    try:
        out = shell('monkey -c android.intent.category.LAUNCHER -v -v 0').split('\n')

        for line in out:
            if "Using main activity" in line:
                pkg = strings.extract_regex_value(line.strip(), r"(?:package ([a-zA-Z0-9_\-].{3,}))")
                if pkg[-1] == ")":
                    pkg = pkg.strip()[0:-1]
                    launcher_apps_list.append(pkg)
    finally:
        return launcher_apps_list


def is_connected_to_network():
    result = shell("dumpsys connectivity")
    return result.find('state: CONNECTED/CONNECTED,') > -1


def airplane_mode(open=True):
    if open:
        shell("settings put global airplane_mode_on 1")
    else:
        shell("settings put global airplane_mode_on 0")


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


def force_stop(pkg):
    return shell("am force-stop " + pkg)


def wait_for_device():
    command.execute("adb", device_serial + ["wait-for-device"])


def get_state():
    return command.execute("adb", args=device_serial + ["get-state"])


def app_is_installed(pkg):
    result = shell("pm path " + pkg)
    return not not result


def get_accounts():
    account_list = []

    result = shell("dumpsys account")

    if result.find("Account {name=") == -1:
        return account_list

    regex_result = strings.extract_regex(result[:result.find("AccountId")], 'name=(.*), type=(.*)}')

    for account in regex_result:
        account_dict = {
            'name': account['sub_groups'][0]['match'],
            'type': account['sub_groups'][1]['match']
        }
        account_list.append(account_dict.copy())

    return account_list


def install_uiautomator2():
    try:
        p = shell("getprop ro.product.cpu.abilist64")
        if not "arm64" in str(p):
            push(os.getcwd() + '/apk/minicap_32','/data/local/tmp/minicap')
            push(os.getcwd() + '/apk/minicap_32.so','/data/local/tmp/minicap.so')
        else:
            push(os.getcwd() + '/apk/minicap_64','/data/local/tmp/minicap')
            push(os.getcwd() + '/apk/minicap_64.so','/data/local/tmp/minicap.so')

        install(os.getcwd() + '/apk/app-uiautomator.apk',option_grant=True)
        install(os.getcwd() + '/apk/app-uiautomator-test.apk', option_grant=True)

        push(os.getcwd() + '/apk/atx-agent','/data/local/tmp')
        push(os.getcwd() + '/apk/minitouch','/data/local/tmp')
        shell('chmod 755 /data/local/tmp/minicap')
        shell('chmod 755 /data/local/tmp/minitouch')
        shell('chmod 755 /data/local/tmp/atx-agent')
        shell('/data/local/tmp/atx-agent server --stop')
        shell('/data/local/tmp/atx-agent server -d')
        return True
    except Exception:
        clear_uiautomator2()
        return False


def clear_uiautomator2():
    uninstall("com.github.uiautomator.test")
    uninstall("com.github.uiautomator")
    shell("rm -rf /data/local/tmp/*")
