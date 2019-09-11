#!/usr/bin/env python
# coding=utf8
from modules import adb
from plugins.soft_plugin import SoftPlugin


class SoftStorage(SoftPlugin):
    def __init__(self, context):
        super(SoftStorage, self).__init__(context)

    def get_AllPartition(self):
        result = []
        partition = adb.shell("mount")
        lines = partition.readlines(partition)
        for line in lines:
            return