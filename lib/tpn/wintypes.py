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
PULONG = POINTER(ULONG)
PVOID = c_void_p
PWSTR = c_wchar_p
PCWSTR = c_wchar_p
PDWORD = POINTER(DWORD)
PFILETIME = POINTER(FILETIME)

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

class FILE_STANDARD_INFO(Structure):
    _fields_ = [
        ('AllocationSize', LARGE_INTEGER),
        ('EndOfFile', LARGE_INTEGER),
        ('NumberOfLinks', DWORD),
        ('DeletePending', BOOLEAN),
        ('Directory', BOOLEAN),
    ]

class CRITICAL_SECTION(Structure):
    _fields_ = []

PCRITICAL_SECTION = POINTER(CRITICAL_SECTION)

class UNICODE_STRING(Structure):
    _fields_ = [
        ('Length', USHORT),
        ('MaximumLength', USHORT),
        ('Buffer', PWSTR),
    ]

PUNICODE_STRING = POINTER(UNICODE_STRING)
PPUNICODE_STRING = POINTER(PUNICODE_STRING)

#===============================================================================
# Functions
#===============================================================================

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
