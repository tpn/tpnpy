#===============================================================================
# Imports
#===============================================================================
import os
import re
from tpn.clipboard import cb

#===============================================================================
# Constants
#===============================================================================
TYPEDEF_RIO_NOTIFICATION_COMPLETION = '''\
typedef struct _RIO_NOTIFICATION_COMPLETION {
  RIO_NOTIFICATION_COMPLETION_TYPE Type;
  union {
    struct {
      HANDLE EventHandle;
      BOOL   NotifyReset;
    } Event;
    struct {
      HANDLE IocpHandle;
      PVOID  CompletionKey;
      PVOID  Overlapped;
    } Iocp;
  };
} RIO_NOTIFICATION_COMPLETION, *PRIO_NOTIFICATION_COMPLETION;'''

CTYPEDEF_RIO_NOTIFICATION_COMPLETION = '''\
    ctypedef struct RIO_NOTIFICATION_COMPLETION:
        RIO_NOTIFICATION_COMPLETION_TYPE Type
        HANDLE EventHandle
        BOOL   NotifyReset
        HANDLE IocpHandle
        PVOID  CompletionKey
        PVOID  Overlapped
    ctypedef RIO_NOTIFICATION_COMPLETION *PRIO_NOTIFICATION_COMPLETION'''

TYPEDEF_XSAVE_FORMAT = '''\
typedef struct DECLSPEC_ALIGN(16) _XSAVE_FORMAT {
    USHORT ControlWord;
    USHORT StatusWord;
    UCHAR TagWord;
    UCHAR Reserved1;
    USHORT ErrorOpcode;
    ULONG ErrorOffset;
    USHORT ErrorSelector;
    USHORT Reserved2;
    ULONG DataOffset;
    USHORT DataSelector;
    USHORT Reserved3;
    ULONG MxCsr;
    ULONG MxCsr_Mask;
    M128A FloatRegisters[8];

#if defined(_WIN64)

    M128A XmmRegisters[16];
    UCHAR Reserved4[96];

#else

    M128A XmmRegisters[8];
    UCHAR Reserved4[224];

#endif

} XSAVE_FORMAT, *PXSAVE_FORMAT;'''

CTYPEDEF_XSAVE_FORMAT = '''\
    ctypedef struct XSAVE_FORMAT:
        USHORT ControlWord
        USHORT StatusWord
        UCHAR TagWord
        UCHAR Reserved1
        USHORT ErrorOpcode
        ULONG ErrorOffset
        USHORT ErrorSelector
        USHORT Reserved2
        ULONG DataOffset
        USHORT DataSelector
        USHORT Reserved3
        ULONG MxCsr
        ULONG MxCsr_Mask
        M128A FloatRegisters[8]
    IF UNAME_MACHINE[-2:] == 'x64':
        M128A XmmRegisters[16]
        UCHAR Reserved4[96]
    ELSE:
        M128A XmmRegisters[8]
        UCHAR Reserved4[224]
    ctypedef XSAVE_FORMAT *PXSAVE_FORMAT'''

#===============================================================================
# Globals
#===============================================================================
DECLSPEC = re.compile('DECLSPEC_[^ ]+ ')

#===============================================================================
# Helpers
#===============================================================================
def convert_windows_typedef_to_cython_ctypedef(text=None, indent_output=True):
    """
    >>> func = convert_windows_typedef_to_cython_ctypedef
    >>> text = TYPEDEF_RIO_NOTIFICATION_COMPLETION
    >>> func(text) == CTYPEDEF_RIO_NOTIFICATION_COMPLETION
    True
    >>> text = TYPEDEF_XSAVE_FORMAT
    >>> func(text) == CTYPEDEF_XSAVE_FORMAT
    True
    """
    from_clipboard = False

    if not text:
        text = cb()
        from_clipboard = True

    lines = text.splitlines()

    first_line = DECLSPEC.sub('', lines[0])

    first_line = (
        first_line.replace('typedef', 'ctypedef')
                  .replace('struct _', 'struct ')
                  .replace('union _', 'union ')
                  .replace('enum _', 'enum ')
                  .replace(' {', ':')
    )

    new_lines = [ first_line, ]
    saw_ifdef = False
    import ipdb
    for line in lines[1:-1]:
        if 'union {' in line:
            continue
        if 'struct {' in line:
            continue
        if 'DUMMY' in line:
            continue
        if '}' in line:
            continue
        if line == '#if defined(_WIN64)':
            line = "IF UNAME_MACHINE[-2:] == 'x64':"
            saw_ifdef = True
            new_lines.append(line)
            continue
        elif line == '#else':
            if saw_ifdef:
                new_lines.append('ELSE:')
            continue
        elif line == '#endif':
            if saw_ifdef:
                saw_ifdef = False
                continue

        line = line.replace(';', '') \
                   .replace(',', '')
        line = DECLSPEC.sub('', line)
        # Strip off bit fields
        ix = line.find(':')
        if ix != -1:
            line = line[:ix]
        #ipdb.set_trace()
        line = line.strip()
        if not line:
            continue
        elif not line.startswith(('IF', 'ELSE', 'ELIF')):
            line = '    %s' % line
        new_lines.append(line)

    typename = first_line.split(' ')[2][:-1]
    last_line = lines[-1]
    ix = last_line.find(',')
    if ix != -1:
        for alias in last_line.split(', ')[1:]:
            line = 'ctypedef %s %s' % (typename, alias.replace(';', ''))
            new_lines.append(line)

    if indent_output:
        sep = '\n    '
        new_lines[0] = '    %s' % new_lines[0]
    else:
        sep = '\n'
    output = sep.join(new_lines)
    if from_clipboard:
        cb(output)
    return output

if __name__ == '__main__':
    import doctest
    doctest.testfile()

# vim:set ts=8 sw=4 sts=4 tw=80 expandtab nospell:                             #
