import abc
import sys
import time
from modules import adb, utils


class Requires(object):
    """
    Decorator used to attach requirements to plugins
    """

    def __init__(self, *args):
        if not args:
            args = []

        for arg in args:
            if arg is None or not issubclass(arg, _Requirement):
                raise ValueError('Invalid argument in @Requires: "{}"'.format(arg))

        self.__requirements = args

    def __call__(self, target):
        target.__requirements__ = self.__requirements
        return target


def validate(reqs, klass):
    klass_reqs = []

    if hasattr(klass, "__requirements__"):
        klass_reqs = klass.__requirements__

    matches = [req for req in reqs if req in klass_reqs]

    return reqs == matches


def conditions_fulfilled(klass):
    if not hasattr(klass, "__requirements__"):
        return True

    for req in klass.__requirements__:
        if not req.check_conditions():
            return False

    return True


def get_requirements_names(klass):
    reqs = klass.__requirements__ if hasattr(klass, "__requirements__") else []
    return utils.get_class_names(reqs)


def get_requirements_classes(reqs=None):
    if reqs is None or len(reqs) == 0:
        return []

    current_mod = sys.modules[__name__]

    return [getattr(current_mod, req) for req in reqs if hasattr(current_mod, req)]


def _check_google_account():
    accounts = adb.get_accounts()

    for account in accounts:
        if account['type'] == 'com.google':
            return True

    return False


def get_weight(klass):
    total_weight = 0

    for req in klass.__requirements__:
        total_weight += req.weight

    return total_weight


def get_instructions(plugin):
    return [req.get_instruction() for req in plugin.__requirements__]


# pseudo enum to use with @Requires
class _Requirement(object):
    __metaclass__ = abc.ABCMeta
    weight = 0

    @staticmethod
    @abc.abstractmethod
    def check_conditions():
        return False

    @staticmethod
    @abc.abstractmethod
    def get_instruction():
        return "Instruction"


class Internet(_Requirement):
    weight = 100

    @staticmethod
    def check_conditions():
        return adb.is_connected_to_network()

    @staticmethod
    def get_instruction():
        return "Device must have Internet connection"


class GoogleAccount(_Requirement):
    weight = 100

    @staticmethod
    def check_conditions():
        return _check_google_account()

    @staticmethod
    def get_instruction():
        return "Device must have at least 1 Google Account"


class NoInternet(_Requirement):
    weight = 0

    @staticmethod
    def check_conditions():
        if adb.is_connected_to_network():
            adb.data_mode()
            adb.wifi_mode()
            time.sleep(1)
        return not adb.is_connected_to_network()

    @staticmethod
    def get_instruction():
        return "Device must have no Internet connection"


class NoGoogleAccount(_Requirement):
    weight = 0

    @staticmethod
    def check_conditions():
        return not _check_google_account()

    @staticmethod
    def get_instruction():
        return "Device must have 0 Google Account."
