#!/usr/bin/env python
# coding=utf8
from modules import adb
from modules import utils
from plugins import soft_gps
from plugins import soft_settings
import os


class AllInfo(object):
    def __init__(self):
        return

    def execute(self):
        self.devices = adb.devices_list
       # self.gps = soft_gps.SoftGps(self)
        self.blue = soft_settings.SoftSettings(self)


if __name__ == "__main__":
    info = AllInfo()
    info.execute()
