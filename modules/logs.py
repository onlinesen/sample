#!/usr/bin/env python
# coding=utf8

import os
import pprint
import time

from colorama import Fore

from modules.singleton import Singleton


@Singleton
class Logs(object):

    def __init__(self):
        self._out_file = None
        self._pp = pprint.PrettyPrinter(indent=4)

    def set_output_file(self, file_path):
        self._out_file = os.path.join(os.sep, file_path, 'report.txt')
        if os.path.isfile(self._out_file):
            os.remove(self._out_file)

    def get_output_file(self):
        return self._out_file

    def info(self, data):
        if type(data) is unicode:
            data = data.encode('utf-8')
        self._log(data, 'I', Fore.GREEN)

    def debug(self, data):
        self._log(data, 'D', Fore.WHITE)

    def warning(self, data):
        self._log(data, 'W', Fore.YELLOW)

    def low_warning(self, data):
        self._log(data, 'W', Fore.BLUE)

    def error(self, data):
        self._log(data, 'E', Fore.RED)

    def print_blue(self, data):
        self._simple_print(data, Fore.BLUE)

    def _simple_print(self, data, color=Fore.RESET):
        if type(data) == str:
            print(color + data + Fore.RESET)
        else:
            self._pp.pprint(data)

    def _log(self, data, t='I', color=Fore.RESET):
        if type(data) == str:
            line = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + t + ' - ' + data
            print(color + line + Fore.RESET)
            self._write_in_file(line)
        else:
            self._pp.pprint(data)

    def _write_in_file(self, line):
        if self._out_file is not None:
            f = open(self._out_file, 'a+')
            f.write(line + "\r\n")
            f.close()
