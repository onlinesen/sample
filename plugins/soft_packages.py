#!/usr/bin/env python
# coding=utf8
from modules import adb, strings
from modules.adb import shell, _display_adb_error
from modules.logs import Logs
from plugins.soft_plugin import SoftPlugin


class SoftPackages(SoftPlugin):
    def __init__(self, context):
        super(SoftPackages, self).__init__(context)
        self.search_packages("com.google.android.gms")

    def search_packages(self, target_package):
        default_package = target_package
        print default_package
        result = shell("pm list packages -f")
        _display_adb_error(result)
        lines = result.split("\n")
        Flag = False

        for line in lines:
            if line:
                name = strings.extract_regex_value(line, '(?:=([a-zA-Z0-9\\-\\._ ]{3,}))')
                if default_package == name:
                    Flag = True
                    break
        print Flag
