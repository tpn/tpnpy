#===============================================================================
# Imports
#===============================================================================
import sys

from win32con import (
    CF_UNICODETEXT,
)

from win32clipboard import (
    OpenClipboard,
    CloseClipboard,
    EmptyClipboard,
    GetClipboardData,
    SetClipboardData,
)

#===============================================================================
# Globals/Aliases
#===============================================================================
is_py3 = sys.version_info.major == 3
if is_py3:
    unicode_class = str
else:
    unicode_class = unicode

#===============================================================================
# Helpers
#===============================================================================

def cb(text=None, fmt=CF_UNICODETEXT, cls=unicode_class, out=None):
    OpenClipboard()
    if not text:
        text = GetClipboardData(fmt)
        CloseClipboard()
        return text
    EmptyClipboard()
    data = cls(text) if cls and not isinstance(text, cls) else text
    SetClipboardData(fmt, data)
    CloseClipboard()
    if not out:
        out = lambda m: sys.stdout.write(m + '\n')
    out("copied %d characters into clipboard..." % len(data))
    return data

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
