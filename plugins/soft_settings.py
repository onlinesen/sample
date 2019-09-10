from modules import adb
from plugins.soft_plugin import SoftPlugin


class SoftSettings(SoftPlugin):
    BT_Initial_state = 1
    WIFI_Initial_state = 1
    NFC_Initial_state = "ON"

    def __init__(self):
        self.initial_configuration()

    # Paddington_MC_3 Initial Power on configuration:  BT, WiFi, and NFC set to 'on '
    def initial_configuration(self, *args):
        bluetooth_state = adb.shell("settings get global bluetooth_on")
        wifi_state = adb.shell("settings get global wifi_on")
        return
