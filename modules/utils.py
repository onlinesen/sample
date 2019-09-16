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


def is_matching_package(package_name, package_pattern):
    if package_pattern is None or package_name is None:
        return False

    if package_pattern.endswith('*'):
        return package_name.startswith(package_pattern.replace('*', ''))
    elif package_pattern.startswith('*'):
        return package_name.endswith(package_pattern.replace('*', ''))
    else:
        return package_name == package_pattern


def merge_dicts(dict1, dict2):
    dictionary = dict1.copy()  # start with x's keys and values
    dictionary.update(dict2)  # modifies z with y's keys and values & returns None
    return dictionary

def str_to_int(value):
    if value is None:
        return None
    else:
        return int(value)