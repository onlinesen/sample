#!/usr/bin/env python
# coding=utf8
from modules import adb
from plugins.soft_plugin import SoftPlugin


class SoftStorage(SoftPlugin):
    def __init__(self, context):
        super(SoftStorage, self).__init__(context)
        self.get_AllPartition()

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


