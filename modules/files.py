#!/usr/bin/env python
# coding=utf8

import os
import re
import shutil
import sys
import zipfile
from os.path import basename
import requests
import urllib3

from modules import strings, utils, errors
from modules.logs import Logs


def get_filename(file_path):
    return basename(file_path)


def get_path(file_path):
    return os.path.dirname(file_path)


def file_get_contents(filename):
    contents = None
    try:
        with open(filename) as f:
            contents = f.read()
    except:
        Logs.instance().error('No such file or directory: ' + filename);
    return contents


def file_exists(path):
    try:
        make_dirs(path)
        os.stat(path)
    except os.error as ex:
        return False
    return True


def is_file_path(path):
    regex = r"(\.[a-z0-9]{2,}$)"
    return strings.match_regex(str(path), regex, re.IGNORECASE)


def folder_from_file_path(file_path):
    return os.path.dirname(os.path.abspath(file_path))


def copy_file(source, destination):
    shutil.copy(source, destination)


def delete_file_if_exists(file_path):
    try:
        if file_exists(file_path):
            os.remove(file_path)
            return True
        return False
    except:
        return False


def delete_directory_if_exists(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        return True
    return False


def fast_rm_file_if_exists(file_path):
    if os.path.exists(file_path):
        if os.path.isdir(file_path):
            children = os.listdir(file_path)

            for child in children:
                fast_rm_file_if_exists(os.path.join(file_path, child))

            os.rmdir(file_path)
        else:
            os.remove(file_path)

    return False


def exists(path,server=False):
    if path is not None:
        if not server:
            return os.path.exists(path)
        else:
            r = requests.get(path).json().get('result')
            return r
    else:
        return False


def make_dirs(filename):
    dir_name = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
            return True
        except OSError as exc:  # Guard against race condition
            Logs.instance().error(exc)
            errors.log_exception_to_file(exc)
            return False
    return False


def find_files(files, dirs=[], extensions=[]):
    new_dirs = []
    for d in dirs:
        try:
            if os.path.isfile(d):
                if extensions is None or os.path.splitext(d)[1] in extensions:
                    files.append(d)
            else:
                new_dirs += [os.path.join(d, f) for f in os.listdir(d)]
        except OSError:
            pass
        except TypeError:
            Logs.instance().warning("Could not reach below " + d + ", skipping to next directory...")

    if new_dirs:
        find_files(files, new_dirs, extensions)
    else:
        return


def list_all_files_recursive(folder):
    files = []
    find_files(files, [folder], None)
    return files


def list_files_recursive(folder, extension):
    files = []
    if not extension.startswith('.'):
        extension = '.' + extension
    find_files(files, [folder], [extension])
    return files


def list_files_recursive_folders(folders, extension):
    files = []
    if not extension.startswith('.'):
        extension = '.' + extension
    find_files(files, folders, [extension])
    return files


def list_files(folder, extension=None, ignore_system=True):
    items = []
    if not exists(folder):
        return items

    result = os.listdir(folder)

    if extension is not None:
        extension = extension.replace('.', '')

    for f in result:
        if extension is not None and f.endswith('.' + extension):
            items.append(f)
        elif extension is None and (not ignore_system or not f.startswith('.')):
            items.append(f)

    return items


def get_file_by_extension(folder, extension):
    items = list_files(folder, extension)
    if len(items) > 0:
        return items[0]
    else:
        return None


def get_path_exec():
    return os.getcwd()


def path_combine(path_start, *path_parts):
    return os.path.join(path_start, *path_parts)


def write_file(file_path, content):
    delete_file_if_exists(file_path)
    f = open(file_path, "a")
    f.write(content)


def write_binary_file(file_path, content):
    delete_file_if_exists(file_path)
    f = open(file_path, "wb")
    f.write(content)


def insert_lines(file_content, content, position=0, new_line=True, trim=False, add_tab=False):
    for item in content:
        if new_line:
            file_content = strings.insert_str(file_content, '\n', position)
            position += 1
            new_line = False

        if add_tab:
            value = "    "  # 4 spaces
        else:
            value = ""

        if trim:
            value += item['match'].strip()
        else:
            value += item['match']

        file_content = strings.insert_str(file_content, '\n' + value, position)
        position += len(value) + 1

    return file_content


def download_file(url, dest, credentials=None):
    """
    Downloads a file using a given config
    :param url: URL of the file to download
    :param dest: Path of the downloaded file
    :param credentials: Credentials to use to download the file,
            should be of the form {'user':'<user>', 'password':'<password>'}
    :return: None
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if credentials is not None:
        basic_auth = credentials['user'] + ':' + credentials['password']
        headers = urllib3.util.make_headers(basic_auth=basic_auth, disable_cache=True)
    else:
        headers = urllib3.util.make_headers(disable_cache=True)

    http = urllib3.PoolManager()
    r = http.request('GET', url, headers=headers, preload_content=False)
    chunk_size = 4096

    header_items = dict(r.headers)

    if 'Content-Length' not in header_items.keys():
        Logs.instance().debug(r.headers)
        Logs.instance().warning('Response has no Content-Length!')
        return None
    total_length = int(header_items['Content-Length'])

    content_filename = url[url.rfind("/") + 1:]

    # check cache:
    if file_exists(dest):
        file_size = os.path.getsize(dest)
        if file_size == total_length:
            Logs.instance().info("File already downloaded in cache!")
            return content_filename
        else:
            delete_file_if_exists(dest)

    Logs.instance().info("Download in progress, please wait...")

    dl = 0
    with open(dest, 'wb') as out:
        while True:
            data = r.read(chunk_size)
            if not data:
                break
            out.write(data)
            dl += len(data)
            done = int(50 * dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
            sys.stdout.flush()

    r.release_conn()
    print("\r")

    return content_filename


def unzip(zip_path, destination):
    # Remove existing source:
    fast_rm_file_if_exists(destination)

    Logs.instance().info("Unzip archive in progress... ")

    try:
        archive = zipfile.ZipFile(zip_path)
        for f in archive.namelist():
            archive.extract(f, destination)
        return True
    except zipfile.BadZipfile:
        msg = "Zip file corrupted: " + str(zip_path)
        Logs.instance().error(msg)
        errors.log_error_to_file(msg)
    return False


def remove_file_ext(filename):
    result, _ = os.path.splitext(filename)
    return result


def get_file_ext(filename):
    _, result = os.path.splitext(filename)
    return result


def path_join_chroot(path, *path_parts):
    parts = []

    for i in range(0, len(path_parts), 1):
        if path_parts[i].startswith("/") or path_parts[i].startswith(os.sep):
            parts.append(path_parts[i][1:])
        else:
            parts.append(path_parts[i])

    return os.path.join(path, *parts)


def fix_sep(path):
    if utils.is_platform_windows():
        return path.replace("/", os.sep)

    return path


FTP_SERVER = '192.168.33.63'
FTP_USER = "anonymous"
import ftplib


def get_ftp_file(ftppath, desc_path):
    try:
        ftp = ftplib.FTP(FTP_SERVER)
        f = os.path.split(ftppath)[0]
        ftp.login(FTP_USER)
        ftp.cwd(f)
        ftp.retrbinary("RETR " + ftppath, open(desc_path, 'wb').write)
        ftp.close()
        return True if file_exists(desc_path) else False
    except Exception as e:
        print(e)
        return False
    finally:
        ftp.close()

