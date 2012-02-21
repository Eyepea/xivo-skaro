# -*- coding: UTF-8 -*-

import argparse
import logging
import functools


def _port_number(value):
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("%r is not a valid port number" % value)
    if port < 1 or port > 65535:
        raise argparse.ArgumentTypeError("%r is not a valid port number" % value)
    return port


def new_argument_parser(add_help=False):
    parser = argparse.ArgumentParser(add_help=add_help)
    parser.add_argument("--listen-port", type=_port_number, default=50030,
                        help="bind to this port")
    parser.add_argument("--listen-addr", default="",
                        help="bind to this address")
    parser.add_argument("--port", type=_port_number, default=5003,
                        help="CTI server port number")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="increase logging verbosity")
    parser.add_argument("hostname",
                        help="CTI server hostname")
    return parser


def init_logging(verbose=False):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    if verbose:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)


def hide_exception(exception_class):
    def hide_exception_decorator(original_function):
        @functools.wraps(original_function)
        def decorated_function(*args, **kwargs):
            try:
                return original_function(*args, **kwargs)
            except exception_class:
                pass
        return decorated_function
    return hide_exception_decorator
