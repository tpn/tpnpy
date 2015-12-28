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
VOID = None
SIZE_T = c_size_t
ULONG_PTR = SIZE_T
LONG_PTR = SIZE_T
DWORD_PTR = SIZE_T
PULONG = POINTER(ULONG)
PVOID = c_void_p
PWSTR = c_wchar_p
PCWSTR = c_wchar_p
PDWORD = POINTER(DWORD)
PFILETIME = POINTER(FILETIME)
SRWLOCK = PVOID
TP_VERSION = DWORD
PTP_POOL = PVOID
PTP_CLEANUP_GROUP = PVOID
PTP_CLEANUP_GROUP_CANCEL_CALLBACK = PVOID
TP_CALLBACK_PRIORITY = DWORD
PACTIVATION_CONTEXT = PVOID

#===============================================================================
# Enums
#===============================================================================
TP_CALLBACK_PRIORITY_HIGH = 0
TP_CALLBACK_PRIORITY_NORMAL = 0
TP_CALLBACK_PRIORITY_LOW = 0
TP_CALLBACK_PRIORITY_INVALID = 0
TP_CALLBACK_PRIORITY_COUNT = TP_CALLBACK_PRIORITY_INVALID

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

class _OVERLAPPED_INNER_STRUCT(Structure):
    _fields_ = [
        ('Offset', DWORD),
        ('OffsetHigh', DWORD),
    ]

class _OVERLAPPED_INNER(Union):
    _fields_ = [
        ('s', _OVERLAPPED_INNER_STRUCT),
        ('Pointer', PVOID),
    ]

class OVERLAPPED(Structure):
    _fields_ = [
        ('Internal', ULONG_PTR),
        ('InternalHigh', ULONG_PTR),
        ('u', _OVERLAPPED_INNER),
        ('hEvent', HANDLE),
    ]
POVERLAPPED = POINTER(OVERLAPPED)
LPOVERLAPPED = POINTER(OVERLAPPED)

class OVERLAPPED_ENTRY(Structure):
    _fields_ = [
        ('lpCompletionKey', ULONG_PTR),
        ('lpOverlapped', LPOVERLAPPED),
        ('Internal', ULONG_PTR),
        ('dwNumberOfBytesTransferred', DWORD),
    ]
POVERLAPPED_ENTRY = POINTER(OVERLAPPED_ENTRY)
LPOVERLAPPED_ENTRY = POINTER(OVERLAPPED_ENTRY)

class TP_CALLBACK_ENVIRON_V3(Structure):
    _fields_ = [
        ('Version', TP_VERSION),
        ('Pool', PTP_POOL),
        ('CleanupGroup', PTP_CLEANUP_GROUP),
        ('CleanupGroupCancelCallback', PTP_CLEANUP_GROUP_CANCEL_CALLBACK),
        ('RaceDll', PVOID),
        ('ActivationContext', PVOID),
        ('FinalizationCallback', PVOID),
        ('Flags', DWORD),
        ('Priority', TP_CALLBACK_PRIORITY),
        ('Size', DWORD),
    ]
TP_CALLBACK_ENVIRON = TP_CALLBACK_ENVIRON_V3


#===============================================================================
# Kernel32
#===============================================================================
kernel32 = ctypes.windll.kernel32

kernel32.CreateThreadpool.restype = PTP_POOL
kernel32.CreateThreadpool.argtypes = [ PVOID, ]

kernel32.SetThreadpoolThreadMinimum.restype = BOOL
kernel32.SetThreadpoolThreadMinimum.argtypes = [ PTP_POOL, DWORD ]

kernel32.SetThreadpoolThreadMaximum.restype = VOID
kernel32.SetThreadpoolThreadMaximum.argtypes = [ PTP_POOL, DWORD ]

kernel32.CloseThreadpool.restype = VOID
kernel32.CloseThreadpool.argtypes = [ PTP_POOL, ]


#===============================================================================
# NtDll
#===============================================================================

#===============================================================================
# Functions
#===============================================================================
def InitializeThreadpoolEnvironmentV3(CallbackEnviron):
    CallbackEnviron.Version = 3
    CallbackEnviron.CallbackPriority = TP_CALLBACK_PRIORITY_NORMAL
    CallbackEnviron.Size = sizeof(TP_CALLBACK_ENVIRON_V3)
InitializeThreadpoolEnvironment = InitializeThreadpoolEnvironmentV3

def SetThreadpoolCallbackLibrary(CallbackEnviron, Threadpool):
    CallbackEnviron.Pool = byref(Threadpool)

def SetThreadpoolCallbackCleanupGroup(CallbackEnviron,
                                      CleanupGroup,
                                      CleanupGroupCancelCallback):
    CallbackEnviron.CleanupGroup = CleanupGroup
    CallbackEnviron.CleanupGroupCancelCallback = CleanupGroupCancelCallback

def SetThreadpoolCallbackActivationContext(CallbackEnviron,
                                           ActivationContext):
    CallbackEnviron.ActivationContext = ActivationContext

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :