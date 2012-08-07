# -*- coding: UTF-8 -*-

import functools
import logging
import time

logger = logging.getLogger(__name__)


def time_decorator(fun):
    fun_name = fun.__name__
    @functools.wraps(fun)
    def aux_fun(*args, **kwargs):
        logger.debug('Entering %s', fun_name)
        start_time = time.time()
        result = fun(*args, **kwargs)
        duration = time.time() - start_time
        logger.debug('Exiting %s (took %.6fs)', fun_name, duration)
        return result
    return aux_fun
