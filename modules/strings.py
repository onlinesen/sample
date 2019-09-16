#!/usr/bin/env python
# coding=utf8

import re


def is_empty(text):
    return text is None or text == ''


def i_replace(text, search, replace):
    regex = re.compile(re.escape(search), re.IGNORECASE)
    return regex.sub(replace, text)


def r_replace(text, regex, replace):
    pattern = re.compile(regex)
    return pattern.sub(replace, text)


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def replace(string_value, old_char, new_char=""):
    if string_value is not None and type(string_value) == str:
        return string_value.replace(old_char, new_char)
    return string_value


def str_contains(string, pattern, case_sensitive=True):
    if string is None or pattern is None:
        return False
    if type(pattern) == str:
        if case_sensitive:
            return pattern in string
        else:
            return pattern.lower() in string.lower()
    else:
        for item in pattern:
            if case_sensitive:
                if item in string:
                    return True
            else:
                if item.lower() in string.lower():
                    return True
        return False


def insert_str(string, str_to_insert, index):
    return string[:index] + str_to_insert + string[index:]


def remove_sub_string(string, start, end):
    result = string[:start] + string[end:]
    return result


def extract_regex_value(content, regex, get_last=False):
    result = extract_regex(content, regex, None)
    # Logs.instance().debug(result)
    if result is not None and len(result) > 0:
        if not get_last:
            return result[0]['sub_groups'][0]['match']
        else:
            return result[(len(result) - 1)]['sub_groups'][0]['match']
    else:
        return None


def match_regex(value, regex, regex_flags=None):
    if value is None or regex is None:
        return False
    if regex_flags is None:
        regex_flags = re.MULTILINE | re.IGNORECASE
    m = re.search(regex, value, regex_flags)
    return m is not None


def contains_regex(content, regex):
    result = extract_regex(content, regex)
    return result is not None and len(result) > 0


def extract_regex(content, regex, excludes=None, regex_flags=None):
    if regex_flags is None:
        regex_flags = re.MULTILINE | re.IGNORECASE

    matches = re.finditer(regex, content, regex_flags)

    result = []

    for matchNum, match in enumerate(matches):

        # matchNum = matchNum + 1
        ignore = False

        sub_groups = []

        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1

            sub_groups.append({'index': groupNum, 'start': match.start(groupNum), 'end': match.end(groupNum),
                               'match': match.group(groupNum)})

        if excludes is not None:
            for exclude in excludes:

                if (match.start() > exclude['start']) & (match.start() < exclude['end']):
                    # print repr(match.start()) + " between [" + repr(exclude['start']) \
                    #      + ", " + repr(exclude['end']) + "]"
                    ignore = True

        if not ignore:
            value = {'start': match.start(), 'end': match.end(), 'match': match.group(), 'sub_groups': sub_groups}
            result.append(value)
        else:
            print("    . Ignore: " + match.group().strip())

    return result


def unicode(value):
    if value.__class__.__name__ == 'str':
        return value.decode('utf-8')
    else:
        return value


def utf8(s):
    if isinstance(s, str):
        return s.encode('utf-8')
    if isinstance(s, (int, float, complex)):
        return str(s).encode('utf-8')
    try:
        return s.encode('utf-8')
    except TypeError:
        try:
            return str(s).encode('utf-8')
        except AttributeError:
            return s
    except AttributeError:
        return s


def snake_to_camel(snake_value=''):
    parts = snake_value.split('_')
    return ''.join(part.title() for part in parts)


def camel_to_snake(camel_value=''):
    return re.sub('(.)([A-Z])', r'\1_\2', camel_value.strip()).lower()


def is_sha256(value):
    regex = r"^(?:[a-z0-9]{2}\:){31}[a-z0-9]{2}$"
    return match_regex(value, regex)


def is_sha1(value):
    regex = r"^(?:[a-z0-9]{2}\:){19}[a-z0-9]{2}$"
    return match_regex(value, regex)


def is_md5(value):
    regex = r"^(?:[a-z0-9]{2}\:){15}[a-z0-9]{2}$"
    return match_regex(value, regex)


def sanitize_for_utf8(value):
    return value.decode('utf-8', 'replace').encode('utf-8')
