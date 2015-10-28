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

from .invariant import (
    PositiveIntegerInvariant,
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

class DedentClipboard(Command):
    """
    Dedents the clipboard by 4 spaces and copies the result back into the
    clipboard.
    """
    times = None
    _times = 1
    class TimesArg(PositiveIntegerInvariant):
        pass
    def run(self):
        from .util import dedent
        from .clipboard import cb
        self._out(cb(dedent(cb())) for i in range(0, self._times))

class IndentClipboard(Command):
    """
    Indents the clipboard by 4 spaces and copies the result back into the
    clipboard.
    """
    count = None
    def run(self):
        from .util import indent
        from .clipboard import cb
        self._out(cb(indent(cb())))

class BitsTable(Command):
    def run(self):
        from .util import bits_table
        self._out(bits_table())

class BitsTable2(Command):
    _shortname_ = 'bt2'
    def run(self):
        from .util import bits_table2
        self._out(bits_table2())

class BitsTable3(Command):
    _shortname_ = 'bt3'
    def run(self):
        from .util import bits_table3
        self._out(bits_table3())

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
