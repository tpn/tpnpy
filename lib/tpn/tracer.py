#===============================================================================
# Imports
#===============================================================================
import sys

import ctypes
from ctypes import *
from ctypes.wintypes import *

from .dll import (
    python,
    tracer,
    pythontracer,
)

from .wintypes import *

#===============================================================================
# Globals/Aliases
#===============================================================================
TRACER = None

#===============================================================================
# Helpers
#===============================================================================

#===============================================================================
# Classes
#===============================================================================
class Tracer:
    def __init__(self,
                 basedir,
                 tracer_dll_path,
                 tracer_rtl_dll_path,
                 tracer_python_dll_path,
                 tracer_pythontracer_dll_path):

        self.basedir = basedir
        self.system_dll = sys.dllhandle

        self.tracer_dll_path = tracer_dll_path
        self.tracer_rtl_dll_path = tracer_rtl_dll_path
        self.tracer_python_dll_path = tracer_python_dll_path
        self.tracer_pythontracer_dll_path = tracer_pythontracer_dll_path

        self.rtl_dll = None
        self.tracer_dll = tracer(self.tracer_dll_path)
        self.tracer_python_dll = python(self.tracer_python_dll_path)
        self.tracer_pythontracer_dll = (
            pythontracer(self.tracer_pythontracer_dll_path)
        )

        self.trace_stores = None
        self.trace_context = None
        self.threadpool = None


    @classmethod
    def create_debug(cls, basedir, conf=None):
        if not conf:
            from .config import get_or_create_config
            conf = get_or_create_config()

        return cls(
            basedir,
            conf.tracer_debug_dll_path,
            conf.tracer_rtl_debug_dll_path,
            conf.tracer_python_debug_dll_path,
            conf.tracer_pythontracer_debug_dll_path,
        )

    @classmethod
    def create_release(cls, basedir, conf=None):
        if not conf:
            from .config import get_or_create_config
            conf = get_or_create_config()

        return cls(
            basedir,
            conf.tracer_dll_path,
            conf.tracer_rtl_dll_path,
            conf.tracer_python_dll_path,
            conf.tracer_pythontracer_dll_path,
        )

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
