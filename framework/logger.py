""" The Logger module of the entire project.
    In addition to the main Logging Class, it contains functions for use as Decorators.
"""
import sys
import os
import inspect
import logging
import logging.handlers
import traceback
import types
from functools import wraps


class Logger:
    """ The main Logger class.
        :param 'name'       by default = 'server' saves in a file of the same name with daily rotation
        :param 'is_debug'   by default = False (do not print in console)
        The main method of Logger generation is 'get_logger'.
        Instead of the standard: LOGGER = logger.getLogger(name)
        use a class call, for example: LOGGER = Logger('tests', is_debug_console=True) or LOGGER = Logger()
        examples of calls:
            logger.critical('Critical message')
            logger.error('Error message')
            logger.warning('Warning message')
            logger.info('Info message')
            logger.debug('Debug message')
    """
    __instance = {}  # for pattern Singleton

    def __new__(cls, name='server', is_debug_console=False, *args, **kwargs):
        """ Use the __new__ method instead of __init__ because it can return an object
            - a shorter initialization of the Class
        """
        LOG_LEVEL = logging.DEBUG if is_debug_console else logging.INFO
        return cls.getInstance(name, LOG_LEVEL)

    @classmethod
    def getInstance(cls, name, log_level):
        """ modified Singleton pattern to eliminate unnecessary parameter assignments,
            although 'logging' has its own Singleton
        """
        if name not in cls.__instance:
            cls.__instance[name] = cls._get_logger(name, log_level)
        return cls.__instance[name]

    @classmethod
    def _get_logger(cls, name, log_level):
        # creating a log shaper (formatter):
        LOG_FORMATTER = logging.Formatter(f'%(asctime)s %(levelname)-8s {cls.get_username()} '
                                          f'%(filename)s %(message)s')
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(cls._get_file_handler(name, LOG_FORMATTER))
        logger.addHandler(cls._get_stream_handler(LOG_FORMATTER, log_level))
        return logger

    @staticmethod
    def _get_file_handler(name, log_formatter):
        FILE_NAME = os.path.join('log', name + '.log')
        if name == 'server':
            # log file rotation every day
            file_handler = logging.handlers.TimedRotatingFileHandler(FILE_NAME, encoding='utf8', interval=1, when='D')
        else:
            file_handler = logging.FileHandler(FILE_NAME, encoding='utf8')
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.DEBUG)
        return file_handler

    @staticmethod
    def _get_stream_handler(log_formatter, log_level):
        # creating log output streams and set level to debug
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(log_level)
        return stream_handler

    @staticmethod
    def get_username():
        # Gives user's home directory
        userhome = os.path.expanduser('~')
        # Gives username by splitting path based on OS
        return os.path.split(userhome)[-1]


""" A block of functions for use as Decorators """


def log_func(func_to_log):
    """Function decorator for functions"""

    @wraps(func_to_log)
    def log_saver(*args, **kwargs):
        # It happens that parameters are passed, but the function does not "wait" for them
        try:
            ret = func_to_log(*args, **kwargs)
        except:
            ret = func_to_log()
        func_name = func_to_log.__name__ if hasattr(func_to_log, '__name__') else \
            func_to_log.name if hasattr(func_to_log, 'name') else ''
        LOGGER.debug(f'The function was called {func_name} with parameters {args}, {kwargs}. '
                     f'Calling from the module {func_to_log.__module__}.'
                     f'Calling from a function {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Calling from a function {inspect.stack()[1][3]}')
        return ret

    return log_saver


def log_class(cls):
    """Decorator function for Classes"""
    for name, method in cls.__dict__.items():
        if not name.startswith('_'):
            if isinstance(method, types.FunctionType) or not hasattr(method, '__func__'):
                setattr(cls, name, method_decorator(method))
            else:  # @staticmethod not callable
                setattr(cls, name, method_decorator(method.__func__, is_static=True))  # доступ с помощью __func__

    return cls


def method_decorator(func_to_log, is_static=False):
    @wraps(func_to_log)
    def wrapper(self, *args, **kwargs):
        func_name = func_to_log.__name__ if hasattr(func_to_log, '__name__') else \
            func_to_log.name if hasattr(func_to_log, 'name') else ''
        args_all = [self].extend(args) if is_static else args
        LOGGER.debug(f'The function was called {func_name} with parameters {args_all}, {kwargs}. '
                     f'Calling from the module {func_to_log.__module__}.'
                     f'Calling from a function {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Calling from a function {inspect.stack()[1][3]}')
        return func_to_log(self, *args, **kwargs)
        # return func_to_log(*args, **kwargs) if is_static else func_to_log(self, *args, **kwargs)

    return wrapper


# create logger for Decorators
LOGGER = Logger('server')
