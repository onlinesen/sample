#!/usr/bin/env python
# coding=utf8
from _socket import timeout
from time import sleep

from selenium.webdriver.common.by import By
from selenium import webdriver
from plugins.soft_plugin import SoftPlugin
from modules import adb
import uiautomator2 as u2


class SoftKeycode(SoftPlugin):
    def __init__(self, context):
        super(SoftKeycode, self).__init__(context)
        self.iput_keycode()

    def iput_keycode(self):
        d = u2.connect("ZT22222882")
        adb.start_activity("com.google.android.dialer", "com.google.android.dialer.extensions.GoogleDialtactsActivity")
        d(resourceId="com.google.android.dialer:id/fab").click()
        code_lines = "*#*#86436#*#*"
        for line in code_lines:
            d(text=line).click()
        counts = len(d(resourceId="android:id/summary"))
        count = 0
        result = {}
        while count < counts:
            key = d(resourceId="android:id/title", instance=count).get_text()
            value = d(resourceId="android:id/summary", instance=count).get_text()
            count = count + 1
            result[key] = value
        print result

