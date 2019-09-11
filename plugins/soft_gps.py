#!/usr/bin/env python
# coding=utf8
from modules import adb
from plugins.soft_plugin import SoftPlugin


class SoftGps(SoftPlugin):
    Gps_Initial_state = "Battery saving"

    def __init__(self, context):
        # super(SoftGps, self).__init__(context)
        super(SoftGps, self).__init__(context)
        self.gps_mode()

    # Paddington_MC_3 GPS should be set to "battery saving"
    def gps_mode(self, *args):
        location_mode = (adb.shell('settings get secure location_providers_allowed')).strip()
        if location_mode == "network":
            result = "Battery saving"
        elif location_mode == "gps":
            result = "Device only"
        else:
            result = "High accuracy"
        self.result = result == self.Gps_Initial_state

