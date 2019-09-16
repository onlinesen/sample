#!/usr/bin/env python
# coding=utf8
from modules import adb, strings
from modules.adb import shell, _display_adb_error
from modules.logs import Logs
from plugins.soft_plugin import SoftPlugin


class SoftPackages(SoftPlugin):
    def __init__(self):
        self.search_packages()

    def search_packages(self):
        default_package = "com.google.android.gms1"
        result = shell("pm list packages -f")
        _display_adb_error(result)
        lines = result.split("\n")

        packages = []
        for line in lines:
            if line:
                name = strings.extract_regex_value(line, '(?:=([a-zA-Z0-9\\-\\._ ]{3,}))')
                if default_package == name:
                    print True
                    break
        print False
