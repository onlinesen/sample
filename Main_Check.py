#!/usr/bin/env python
# coding=utf8
from modules import adb
from modules import utils
import os


class AllInfo(object):
    def __init__(self):
        return

    def execute(self):
        self.devices = adb.devices_list
        print len(self.devices)


if __name__ == "__main__":
    info = AllInfo()
    info.execute()
