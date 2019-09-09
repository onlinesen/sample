#!/usr/bin/env python
# coding=utf8

import sys


def get_options():
    options = {}
    args = sys.argv
    option = None

    for arg in args:
        if option is not None:
            if not arg.strip().startswith('-'):
                options[option] = arg.strip()
            option = None

        if arg.strip().startswith('-'):
            option = arg.strip()
            options[option] = None

    return options


def get_option_value(option, default_value=None):
    options = get_options()
    if option in options:
        return options[option]
    else:
        return default_value


def has_option(option):
    items = get_options()
    result = False
    for item in items:
        if option == items:
            result = True
            break
    return result
