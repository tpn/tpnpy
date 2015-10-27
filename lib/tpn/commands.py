#===============================================================================
# Imports
#===============================================================================
import sys

import textwrap

from .util import strip_linesep_if_present

from .command import (
    Command,
    CommandError,
)

#===============================================================================
# Commands
#===============================================================================

class HelloWorld(Command):
    def run(self):
        self._out('Hello, World!')

class ClipBoardCopy(Command):
    """Copies stdin into the clipboard."""
    _shortname_ = 'cc'
    def run(self):
        from .clipboard import cb
        text = strip_linesep_if_present(sys.stdin.read()).rstrip()
        cb(text=text, out=self._out)

class ClipBoardPaste(Command):
    """Pastes the contents of the clipboard to stdout."""
    _shortname_ = 'pp'
    def run(self):
        from .clipboard import cb
        self._out(cb(text=None))

class WindowsTypedefToCythonCtypedefFromClipboard(Command):
    """
    Converts the contents of the clipboard (which is a copy of a Windows header
    typedef) into the Cython ctypedef representation, then replace the clipboard
    with that entry.
    """
    _shortname_ = 'wtc'
    def run(self):
        from .convert import convert_windows_typedef_to_cython_ctypedef
        output = convert_windows_typedef_to_cython_ctypedef()
        self._out(output)

class WindowsFuncdefToCythonFuncdefFromClipboard(Command):
    """
    Converts the contents of the clipboard (which is a copy of a Windows header
    function definition) into the Cython ctypedef representation, then replace
    the clipboard with that entry.
    """
    _shortname_ = 'wfc'
    def run(self):
        from .convert import convert_windows_funcdef_to_cython_funcdef
        output = convert_windows_funcdef_to_cython_funcdef()
        self._out(output)

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
