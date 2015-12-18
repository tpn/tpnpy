#===============================================================================
# Imports
#===============================================================================
import sys
import ctypes

from ctypes import *
from ctypes.wintypes import *

#===============================================================================
# Globals/Aliases
#===============================================================================
PVOID = c_void_p
PCWSTR = c_wchar_p

#===============================================================================
# Classes
#===============================================================================
class GUID(Structure):
    _fields_ = [
        ('Data1',   LONG),
        ('Data2',   SHORT),
        ('Data3',   SHORT),
        ('Data4',   BYTE * 8),
    ]

class TRACE_SESSION(Structure):
    _fields_ = [
        ('Size',            DWORD),
        ('SessionId',       LARGE_INTEGER),
        ('MachineGuid',     GUID),
        ('Sid',             PVOID),
        ('UserName',        PCWSTR),
        ('ComputerName',    PCWSTR),
        ('DomainName',      PCWSTR),
        ('SystemTime',      FILETIME),
    ]

class TRACE_CONTEXT(Structure):
    _fields_ = [
        ('Size',            DWORD),
        ('TraceSession',    POINTER(TRACE_SESSION)),
        ('TraceStores',     PVOID),
        ('TraceCallback',   PVOID),
    ]


#===============================================================================
# Functions
#===============================================================================
def vspyprof(path=None, dll=None):
    assert path or dll
    if not dll:
        dll = ctypes.PyDLL(path)

    dll.CreateProfiler.restype = c_void_p
    dll.CreateCustomProfiler.restype = c_void_p
    dll.CreateCustomProfiler.argtypes = [c_void_p, ctypes.c_void_p]
    dll.CloseThread.argtypes = [c_void_p]
    dll.CloseProfiler.argtypes = [c_void_p]
    dll.InitProfiler.argtypes = [c_void_p]
    dll.InitProfiler.restype = c_void_p

    #dll.SetTracing.argtypes = [c_void_p]
    #dll.UnsetTracing.argtypes = [c_void_p]
    #dll.IsTracing.argtypes = [c_void_p]
    #dll.IsTracing.restype = c_bool

    return dll

def pytrace(path=None, dll=None):
    assert path or dll
    dll = vspyprof(path, dll)

    dll.CreateTracer.restype = PVOID
    dll.CreateTracer.argtypes = [PVOID, PVOID]

    return dll

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
