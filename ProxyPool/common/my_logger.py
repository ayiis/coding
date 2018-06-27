#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import logging, traceback

__all__ = ["LOGGING_LEVEL", "LOGGING_MOD", "Logger"]

# logging.debug     10
# logging.info      20
# logging.warn      30
# logging.warning   30
# logging.error     40
# logging.critical  50

# DISABLED logging.log       0
# DISABLED logging.exception 40
LOGGING_LEVEL = 10

# a: append, w: write
LOGGING_MOD = "w"


def Logger(logger_name, output_to_console=False, output_to_all=True, extra_addon=True):

    logger = logging.getLogger(logger_name)
    logger.propagate = False    # work for this logger alone

    formatter = logging.Formatter("%(asctime)s:%(filename)s-L%(lineno)d-%(levelname)s: %(message)s")
    file_formatter = logging.Formatter("%(asctime)s -%(module)s:%(filename)s-L%(lineno)d-%(levelname)s: %(message)s")

    fileHandler = logging.FileHandler("./logs/%s.log.txt" % logger_name, LOGGING_MOD)
    fileHandler.setFormatter(file_formatter)
    logger.addHandler(fileHandler)

    if output_to_console:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)

    if output_to_all:
        fileHandler_all = logging.FileHandler("./logs/all.log")
        fileHandler_all.setFormatter(file_formatter)
        logger.addHandler(fileHandler_all)

    logger.setLevel(LOGGING_LEVEL)
    # logger.info("Current log \"%s\", log level is : %s", logger_name, logging.getLevelName(logger.getEffectiveLevel()))

    if extra_addon:
        setattr(logger, "findCaller", my_findCaller)
        setattr(logger, "my_debug", lambda *msg: my_debug(logger, *msg))
        setattr(logger, "my_error", lambda *msg: my_error(logger, *msg))
        setattr(logger, "my_exc", lambda *msg: my_exc(logger, *msg))

        function_encode_str(logger)

    return logger


# To get the caller of `func in function_encode_str`
def my_findCaller():
    """
    Find the stack frame of the caller so that we can note the source
    file name, line number and function name.
    """
    import sys, os

    f = sys._getframe(3)
    #On some versions of IronPython, currentframe() returns None if
    #IronPython isn"t run with -X:Frames.
    if f is not None:
        f = f.f_back
    rv = "(unknown file)", 0, "(unknown function)"
    if hasattr(f, "f_code"):
        co = f.f_code
        filename = os.path.normcase(co.co_filename)
        rv = (co.co_filename, f.f_lineno, co.co_name)
    return rv


def encode_args_encode(*msg):
    return " ".join([m.encode("utf-8") if isinstance(m, unicode) else str(m) for m in msg])


def function_encode_str(logger):
    for func_name in ["debug", "info", "warning", "error", "critical"]:
        setattr(logger, func_name,  (lambda logger, func: lambda *msg: func( encode_args_encode(*msg) ) )(logger, getattr(logger, func_name)))


def my_debug(logger, *msg):
    logger.debug("Traceback stack DEBUG \r\n%s\r\n%s\r\n------" % ("-".join(traceback.format_stack()[:-2]), encode_args_encode(*msg)))


def my_error(logger, *msg):
    logger.error("Traceback stack ERROR \r\n%s\r\n%s\r\n------" % ("+".join(traceback.format_stack()[:-2]), encode_args_encode(*msg)))


def my_exc(logger, *msg):
    logger.critical("Traceback stack EXCEPTION \r\n%s\r\n%s\r\n%s\r\n------" % (">".join(traceback.format_stack()[:-2]), traceback.format_exc(), encode_args_encode(*msg)))
