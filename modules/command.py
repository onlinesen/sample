#!/usr/bin/env python
# coding=utf8

import subprocess
from modules.logs import Logs

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os


def execute(cmd, args=None, display_cmd=False, disable_out=False, disable_error=False, no_wait=False, is_shell=False):
    if cmd is None:
        return None

    cmd_args = [cmd]

    if args is not None:
        for arg in args:
            cmd_args.append(str(arg))

    if display_cmd:
        str_cmd = None
        for arg in cmd_args:
            if str_cmd is None:
                str_cmd = str(arg)
            else:
                str_cmd = str_cmd + " " + str(arg)
        Logs.instance().debug(str_cmd)

    std_out = subprocess.PIPE
    if disable_out:
        std_out = DEVNULL
        # std_out = open(os.devnull, 'wb')

    if no_wait:
        subprocess.Popen(cmd_args, stdin=None, stdout=None, stderr=None, shell=is_shell)
        return None
    elif disable_error:
        p = subprocess.Popen(cmd_args, stdout=std_out, stderr=DEVNULL, shell=is_shell)
    else:
        p = subprocess.Popen(cmd_args, stdout=std_out, stderr=subprocess.STDOUT, shell=is_shell)

    if disable_out:
        return None
    else:
        out = p.stdout.read().decode('utf-8')
        return out

