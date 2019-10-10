#!/usr/bin/env python
# coding=utf8
from time import sleep

from plugins.soft_plugin import SoftPlugin
from modules import adb, constants


class SoftHardKey(SoftPlugin):
    def __init__(self, context):
        super(SoftHardKey, self).__init__(context)
        adb.start_activity(constants.Constants.CAMERA[0], constants.Constants.CAMERA[1])
        self.volume_up()
        sleep(5)
        self.volume_down()
        pass

    def volume_up(self):
        adb.input_keyevent("24")

    def volume_down(self):
        adb.input_keyevent("25")

    def power(self):
        adb.input_keyevent("26")

    def wakes_up_screen(self):
        adb.input_keyevent("224")

    def end_call(self):
        adb.input_keyevent("6")

    def take_photos(self):
        adb.input_keyevent("27")


