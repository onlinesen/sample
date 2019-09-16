#!/usr/bin/env python
# coding=utf8
from modules import adb
from modules import utils
from plugins import soft_gps, soft_storage
from plugins import soft_settings
from plugins import soft_packages
import os


class AllInfo(object):
    def __init__(self):
        return

    def execute(self):
        self.devices = adb.devices_list
       # self.gps = soft_gps.SoftGps(self)
       # self.blue = soft_settings.SoftSettings(self)
        #self.storage = soft_storage.SoftStorage(self)
        self.package = soft_packages.SoftPackages()


if __name__ == "__main__":
    info = AllInfo()
    info.execute()
