#!/usr/bin/env python
# coding=utf8

import logging
import os
import sys
import time
import traceback

current_module = sys.modules[__name__]

software = None
report_manager = None
report_path = None


def init(soft, rep_manager, rep_path):
    current_module.software = soft
    current_module.report_manager = rep_manager
    current_module.report_path = rep_path


def __get_log_filename():
    return "errors-" + time.strftime("%Y%m%d_%H%M") + ".log"


def __add_handlers(logger):
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    formatter = logging.Formatter("%(asctime)s - %(levelname)-12s %(message)s")

    log_path = os.path.join(root_path, "logs", __get_log_filename())

    if not os.path.exists(os.path.dirname(log_path)):
        os.mkdir(os.path.dirname(log_path))

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def __print_session_start(logger):
    logger.info("")
    logger.info("===================")
    logger.info("== Session start ==")
    logger.info("===================")
    logger.info("")


def log_exception_to_file(ex):
    __err_logger.exception("Exception: {0}\n".format(str(ex)))


def log_error_to_file(err):
    __err_logger.error("Error: {0}\n".format(str(err)))


def print_analysis_id(analysis_id):
    __err_logger.info("Analysing " + analysis_id + "\n")


# This function is already defined in module Files.
# In order to prevent cyclic imports (Module files import this module)
# we redefine this function in this module.
def __path_combine(path_start, *path_parts):
    return os.path.join(path_start, *path_parts)


def __update_soft_analysis_status(status):
    current_module.software['analysis_status'] = status
    current_module.software['_id'] = current_module.report_manager.add_software(
        __path_combine(current_module.report_path, 'software', 'software.json'), current_module.software)


def except_hook(ex_type, ex_value, ex_traceback):
    if issubclass(ex_type, KeyboardInterrupt):
        if current_module.software and current_module.report_manager:
            __update_soft_analysis_status({"status": 'Analysis canceled'})
        sys.__excepthook__(ex_type, ex_value, ex_traceback)
        return

    elif current_module.software and current_module.report_manager:
        tb = traceback.extract_tb(ex_traceback)
        my_stack = []

        for elem in tb:
            my_stack.append(
                ("File " + elem[0] + " , line " + str(elem[1]) +
                 " , in " + elem[2] + " => " + elem[3]).replace('\\', '/'))

        __update_soft_analysis_status({
            "status": "Analysis crashed.",
            "type": str(ex_type),
            "value": str(ex_value),
            "traceback": my_stack
        })

    __err_logger.critical("Uncaught exception:", exc_info=(ex_type, ex_value, ex_traceback))
    logging.critical("Uncaught exception:", exc_info=(ex_type, ex_value, ex_traceback))


__err_logger = logging.getLogger(__name__)
__err_logger.setLevel(logging.INFO)
__add_handlers(__err_logger)
__print_session_start(__err_logger)
