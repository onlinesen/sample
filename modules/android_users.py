#!/usr/bin/env python
# coding=utf8

import xml.etree.ElementTree as ET

from modules import files


def get_xml_android_users(file_path):
    content = files.file_get_contents(file_path)
    resources = ET.fromstring(content)

    items = []

    for child in resources.findall('.//item'):

        item = {}
        item['value'] = 0
        item['tag'] = None
        item['description'] = None

        for sub_child in child.findall('.//'):
            if (sub_child.text is not None) and ((sub_child.text.lower() == 'true') or (sub_child.text == '1')):
                item[sub_child.tag] = True
            elif (sub_child.text is not None) and ((sub_child.text.lower() == 'false') or (sub_child.text == '0')):
                item[sub_child.tag] = False
            else:
                item[sub_child.tag] = sub_child.text

        if item['value'] is not None and item['value'] != '':
            items.append(item)

    # Logs.instance().debug(items)
    return items


def get_android_users_list(root_path):
    path = files.path_combine(root_path, 'resources')
    file_items = files.list_files(path)

    xml_list = []
    for f in file_items:
        if f.startswith('android-users'):
            xml_list.append(f)

    # Logs.instance().debug(xml_list)

    users_list = []
    for xml in xml_list:
        xml_path = files.path_combine(path, xml)
        items = get_xml_android_users(xml_path)
        for item in items:
            users_list.append(item)

    return users_list
