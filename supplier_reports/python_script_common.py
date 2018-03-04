"""
common utilities for short scripts
"""

import logging, os
import subprocess, sys
import inspect
import traceback, pdb
import functools
import inspect

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse
import random, string

_logger = logging.getLogger(__name__)

##################################################
# logging
##################################################


def get_logger_for_level(level):
    def log(self, message, *args, **kws):
        if self.isEnabledFor(level):
            self._log(level, message, args, **kws)
    return log


def add_logging_levels():
    levels = {"NOTE":25, "TRACE": 5}
    for level_name, level in levels.items():
        logging.addLevelName(level, level_name)
        setattr(logging.Logger,level_name.lower() , get_logger_for_level(level))
        setattr(logging, level_name,level)

add_logging_levels()

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s.%(lineno)d] -- %(message)s")

def add_handler(logger, handler_inst, formatter=formatter, level=logging.NOTSET):
    #we only add handlers to root loggers
    handler_inst.setLevel(level)
    handler_inst.setFormatter(formatter)
    logger.addHandler(handler_inst)

def get_console_level(verbose):
    if verbose == 0:
        console_level = logging.NOTE
    elif verbose == 1:
        console_level = logging.INFO
    elif verbose == 2:
        console_level = logging.DEBUG
    else: # >2
        console_level = logging.TRACE
    return console_level

def set_logging(app_name=None, app_path=None, verbose=0, file_handler=True):
    root_logger=logging.getLogger()
    root_logger.setLevel(logging.TRACE) #forcing the lowest effective level from WARN
    console_level = get_console_level(verbose)
    add_handler(root_logger, logging.StreamHandler(), level=console_level)

    if file_handler:
        #file_name
        caller_dirname, caller_filename = get_caller_dir_and_file()
        filename_no_ext = os.path.splitext(caller_filename)[0]
        app_path = caller_dirname if app_path is None else app_path
        app_name = filename_no_ext if app_name is None else app_name
        log_file_path = os.path.join(app_path, app_name + '.log')

        if console_level == logging.TRACE:
            _logger.warn("#### TRACE is on ####")
            file_handler_level = logging.TRACE
        else:
            file_handler_level = logging.DEBUG
        add_handler(root_logger, logging.FileHandler(log_file_path), level=file_handler_level)
        _logger.debug("log path: {}".format(log_file_path))
        return log_file_path


##################################################
# other
##################################################

def trace_call(f):
    @functools.wraps(f)
    def trace_func_call(*args, **kwargs):
        returned = f(*args, **kwargs)
        _logger.trace(get_funcall_string(f,args,kwargs,returned))
        return returned
    return trace_func_call

def get_caller_dir_and_file():
    frame_info = inspect.stack()[2]
    frame = frame_info[0]
    mod = inspect.getmodule(frame)
    dirname = os.path.dirname(os.path.abspath(mod.__file__))
    filename = os.path.basename(mod.__file__)
    return dirname, filename

def repr_arg(arg, size=30):
    args=str(arg)
    if len(args)<size:
        return "<arg: {}>".format(arg)
    else:
        return "<longarg: {}, len:{}>".format(args[:30], len(args))

def get_funcall_string(f,args,kwargs,returned):
    kwargs_str = "," + str(kwargs)[1:-1] if kwargs else ""
    arglist = list(args)
    if f.__qualname__.find(".") != -1:  # inspect.ismethod(f):
        arglist = arglist[1:]
    return "{}({}{})={}".format(f.__qualname__, ",".join(map(repr_arg,arglist)), kwargs_str,returned)


def get_file_name(file_path, with_ext=True):
    file_name = os.path.split(file_path)[1]
    if with_ext:
        return file_name
    else:
        return file_name.split(".")[0]


def run_command(cmd, communicate=True):
    _logger.debug("run_command: '{}'".format(cmd))
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if communicate:
        stdout, stderr = process.communicate()
        _logger.debug("run_command returncode: {}".format(process.returncode))
        return process.returncode, stdout, stderr
    else:
        return process.wait()


def run_command_assert_success(cmd):
    returncode, stdout, stderr = run_command(cmd)
    assert returncode == 0, "failed to exec cmd:'{}' ret:'{}' error:'{}'".format(cmd, returncode, stderr)
    return stdout


def info(type, value, tb):
    """ exception handler

    how to set: sys.excepthook = info


    :param type:
    :param value:
    :param tb:
    :return:
    """
    if hasattr(sys, 'ps1') or not sys.stderr.isatty():
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook
        sys.__excepthook__(type, value, tb)
    else:
        import traceback, pdb
        # we are NOT in interactive mode, print the exception...
        # traceback.print_exception(type, value, tb)
        # print
        # ...then start the debugger in post-mortem mode.
        pdb.pm()


def generate_random_name(length=5):
    return "".join([random.choice(string.ascii_letters) for x in range(length)])


def guess_file_name_from_url(url):
    u = urlparse(url)
    if u.path.split("/") > 1:
        return u.path.split("/")[-1]
    else:
        return generate_random_name(5)


