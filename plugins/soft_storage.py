#!/usr/bin/env python
# coding=utf8
from time import sleep

from modules import adb
from plugins.soft_plugin import SoftPlugin
from modules import constants
import uiautomator2 as u2


class SoftStorage(SoftPlugin):
    def __init__(self, context):
        super(SoftStorage, self).__init__(context)
        d = u2.connect("ZT22222882")
        d.press("home")
        sleep(1)
        adb.start_activity(constants.Constants.SETTINGS[0], constants.Constants.SETTINGS[1])
        sleep(1)
        d(text="Storage").click()
        sleep(1)
        counts = len(d(resourceId="android:id/summary"))
        print counts
        count = 1
        result = {}
        while count < counts:
            key = d(resourceId="android:id/title", instance=count+1).get_text()
            value = d(resourceId="android:id/summary", instance=count).get_text()
            count = count + 1
            result[key] = value
        if result.has_key("Internal shared storage") & result.has_key("SD card"):
            print True

    def get_AllPartition(self):
        result = adb.shell("df -h")
        lines = result.split("\n")
        cache_available = None
        root_available = None

        for line in lines:
            if "cache" in line:
                data = line.split("\t")
                cache_result = data[0].split()
                cache_available = cache_result[3]
            elif "root" in line:
                data = line.split("\t")
                root_partition = data[0].split()
                root_available = root_partition[3]
        print cache_available
        print root_available
