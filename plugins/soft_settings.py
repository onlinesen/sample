#!/usr/bin/env python
# coding=utf8
from modules import adb
from modules.logs import Logs
from plugins.soft_plugin import SoftPlugin


class SoftSettings(SoftPlugin):
    BT_Initial_state = "1"
    WIFI_Initial_state = 1
    NFC_Initial_state = "ON"

    def __init__(self, context):
        super(SoftSettings, self).__init__(context)
        self.initial_bluetooth()

    # Paddington_MC_3 Initial Power on configuration:  BT, WiFi, and NFC set to 'on '
    def initial_bluetooth(self, *args):
        bluetooth_state = adb.shell("settings get global bluetooth_on")
        self.result = bluetooth_state == self.BT_Initial_state
        if not self.result:
            Logs.instance().info("BT is disable")
            return

    def initial_wifi(self, *args):
        wifi_state = adb.shell("settings get global wifi_on")
        self.result = wifi_state == self.BT_Initial_state
        if not self.result:
            Logs.instance().info("wifi is disable")
            return

