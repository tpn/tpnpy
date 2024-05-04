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
    BoolInvariant,
    PathInvariant,
    StringInvariant,
    DirectoryInvariant,
    MkDirectoryInvariant,
    PositiveIntegerInvariant,
)

from .commandinvariant import (
    InvariantAwareCommand,
)

#===============================================================================
# Commands
#===============================================================================

class DoctestCommand(Command):
    _shortname_ = 'dt'
    def run(self):
        self._out("running doctests...")
        quiet = self.options.quiet
        import doctest
        import tpn.util
        import tpn.logic
        verbose = not quiet
        doctest.testmod(tpn.util, verbose=verbose, raise_on_error=True)
        doctest.testmod(tpn.logic, verbose=verbose, raise_on_error=True)

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

class WindowsTypedefToPythonCtypesStructureFromClipboard(Command):
    """
    Converts the contents of the clipboard (which is a copy of a Windows header
    typedef) into the Cython ctypedef representation, then replace the clipboard
    with that entry.
    """
    _shortname_ = 'wtcs'
    def run(self):
        from .convert import convert_windows_typedef_to_python_ctypes_structure
        output = convert_windows_typedef_to_python_ctypes_structure()
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

class VsProfileProgram(InvariantAwareCommand):
    """
    Runs the vspyprof against the given file.
    """
    _verbose_ = True

    python_file = None
    _python_file = None
    class PythonFileArg(PathInvariant):
        _help = "Path to the Python file to profile"
        _mandatory = True

    python_exe = None
    _python_exe = None
    class PythonExeArg(PathInvariant):
        _help = (
            "Path to the Python interpreter to use.  Defaults to "
            "[ptvs:python_exe], or if that's not set, whatever "
            "sys.executable is."
        )
        _mandatory = False

    program_args = None
    class ProgramArgsArg(StringInvariant):
        _help = (
            "Additional list of arguments to pass to the Python "
            "file being profiled.  (XXX: Not Yet Implemented.)"
        )
        _mandatory = False

    vspyprof_dll = None
    class VspyprofDllArg(PathInvariant):
        _help = (
            "Path to the Visual Studio Profiler DLL "
            "(defaults to [ptvs:dll] in config file)."
        )
        _mandatory = False

    use_debug_dlls = None
    class UseDebugDllsArg(BoolInvariant):
        _help = "Use the debug versions of profiler DLLs."
        _mandatory = False
        _default = False

    trace = None
    class TraceArg(BoolInvariant):
        _help = "Enable tracing (instead of profiling)."
        _mandatory = False
        _default = False

    custom_profiler_dll = None
    class CustomProfilerDllArg(PathInvariant):
        _help = (
            "Optional path to a custom profile DLL to use instead of the "
            "Visual Studio vsperf.dll that vspyprof.dll was built against. "
            "This must export C __stdcall symbols for EnterFunction, "
            "ExitFunction, NameToken and SourceLine.  (See PythonApi.cpp "
            "in PTVS for more info.)"
        )
        _mandatory = False

    pause_before_starting = None
    class PauseBeforeStartingArg(BoolInvariant):
        _help = (
            "If set to true, pauses prior to starting profiling.  This allows "
            "you to independently attach debuggers, etc."
        )
        _default = False
        _mandatory = False

    run_dir = None
    _run_dir = None
    class RunDirArg(DirectoryInvariant):
        _help = "Directory to run the profiler from."

    def run(self):
        InvariantAwareCommand.run(self)

        conf = self.conf
        dll = self.options.profiler_dll
        if not dll:
            if self.options.use_debug_dlls:
                dll = conf.ptvs_debug_dll_path
            else:
                dll = conf.ptvs_dll_path

        custdll = self.options.custom_profiler_dll
        if not custdll:
            if self.options.use_debug_dlls:
                custdll = conf.ptvs_custom_debug_dll_path
            else:
                custdll = conf.ptvs_custom_dll_path
        self._verbose("Using profiler DLL: %s" % dll)
        if custdll:
            self._verbose("Using custom profiler DLL: %s" % custdll)
        else:
            custdll = '-'
        from . import vspyprof

        from .util import chdir
        from .path import join_path
        from os.path import dirname

        import sys

        this_dir = dirname(__file__)
        runvspyprof = join_path(this_dir, 'runvspyprof.py')

        exe = self._python_exe or conf.ptvs_python_exe

        cmd = [
            exe,
            runvspyprof,
            dll,
            self._run_dir,
            custdll,
            self._python_file,
        ]

        program_args = self.options.program_args
        if program_args:
            import shlex
            args = shlex.split(program_args)
            cmd.append(args)

        if self.options.pause_before_starting:
            import msvcrt
            sys.stdout.write('Press any key to continue . . .')
            sys.stdout.flush()
            msvcrt.getch()

        import os
        env = os.environ
        if self.options.trace:
            env['VSPYPROF_TRACE'] = '1'

        env['VSPYPROF_DEBUGBREAK_ON_START'] = '1'

        import subprocess
        with chdir(this_dir):
            subprocess.call(cmd, env=env)

class TestVsPyProfTraceStores(InvariantAwareCommand):
    """
    Runs the vspyprof against the given file.
    """
    _verbose_ = True

    python_file = None
    _python_file = None
    class PythonFileArg(PathInvariant):
        _help = "Path to the Python file to profile"
        _mandatory = True

    python_exe = None
    _python_exe = None
    class PythonExeArg(PathInvariant):
        _help = (
            "Path to the Python interpreter to use.  Defaults to "
            "[ptvs:python_exe], or if that's not set, whatever "
            "sys.executable is."
        )
        _mandatory = False

    program_args = None
    class ProgramArgsArg(StringInvariant):
        _help = (
            "Additional list of arguments to pass to the Python "
            "file being profiled.  (XXX: Not Yet Implemented.)"
        )
        _mandatory = False

    vspyprof_dll = None
    class VspyprofDllArg(PathInvariant):
        _help = (
            "Path to the Visual Studio Profiler DLL "
            "(defaults to [ptvs:dll] in config file)."
        )
        _mandatory = False

    use_debug_dlls = None
    class UseDebugDllsArg(BoolInvariant):
        _help = "Use the debug versions of profiler DLLs."
        _mandatory = False
        _default = False

    trace = None
    class TraceArg(BoolInvariant):
        _help = "Enable tracing (instead of profiling)."
        _mandatory = False
        _default = False

    custom_profiler_dll = None
    class CustomProfilerDllArg(PathInvariant):
        _help = (
            "Optional path to a custom profile DLL to use instead of the "
            "Visual Studio vsperf.dll that vspyprof.dll was built against. "
            "This must export C __stdcall symbols for EnterFunction, "
            "ExitFunction, NameToken and SourceLine.  (See PythonApi.cpp "
            "in PTVS for more info.)"
        )
        _mandatory = False

    pause_before_starting = None
    class PauseBeforeStartingArg(BoolInvariant):
        _help = (
            "If set to true, pauses prior to starting profiling.  This allows "
            "you to independently attach debuggers, etc."
        )
        _default = False
        _mandatory = False

    base_dir = None
    _base_dir = None
    class BaseDirArg(DirectoryInvariant):
        _help = "Base directory to pass to tracer"

    dll = None

    def run(self):
        InvariantAwareCommand.run(self)

        conf = self.conf
        dllpath = self.options.profiler_dll
        if not dllpath:
            if self.options.use_debug_dlls:
                dllpath = conf.ptvs_debug_dll_path
            else:
                dllpath = conf.ptvs_dll_path

        import ctypes
        from .wintypes import DWORD
        from .dll import pytrace

        dll = pytrace(path=dllpath)

        basedir = ctypes.c_wchar_p(self._base_dir)

        size = dll.GetTraceStoresAllocationSize()
        stores = ctypes.create_string_buffer(size)

        import pdb
        if self.options.pause_before_starting:
            dll.Debugbreak()
            import pdb
            pdb.set_trace()

        dll.InitializeTraceStores(
            basedir,
            ctypes.pointer(stores),
            ctypes.byref(size),
            ctypes.c_void_p(0),
        )

        import ipdb
        ipdb.set_trace()
        self.dll = dll


class ArchiveUntrackedFiles(InvariantAwareCommand):
    """
    Archives all untracked files in the current directory.
    """

    path = None
    _path = None
    class PathArg(MkDirectoryInvariant):
        _help = "Path to the archive directory."
        _mandatory = True

    def run(self):
        InvariantAwareCommand.run(self)
        import os
        from .util import archive_untracked_git_files
        archive_untracked_git_files(os.getcwd(), self._path)

class PrintPytestFailures(InvariantAwareCommand):
    """
    Parses a given pytest-results.xml file, prints a tabular summary of test
    failures, and saves full failure details in .json and .txt format.
    """

    path = None
    _path = None
    class PathArg(PathInvariant):
        _help = "path of pytest-results.xml file"

    no_fancy_unicode_chars = None
    class NoFancyUnicodeCharsArg(BoolInvariant):
        _help = "use normal ASCII chars instead of fancy Unicode counterparts"
        _mandatory = False
        _default = False

    def run(self):
        out = self._out
        options = self.options
        verbose = self._verbose

        path = self._path

        from .util import (
            render_text_table,
            render_fancy_text_table,
            Dict,
        )

        from itertools import (
            chain,
            repeat,
        )

        import json
        from textwrap import (
            dedent,
            indent,
        )
        from xml.etree import ElementTree

        tree = ElementTree.parse(path)
        root = tree.getroot()
        elements = tree.findall('.//testcase/[failure]')

        dicts = []
        rows = [(
            'Index',
            'Start Time',
            'Module',
            'Run Time',
            'Failure',
        )]
        #import ipdb
        #ipdb.set_trace()

        for (i, e) in enumerate(elements, start=1):
            # Example attributes:
            # {'classname': 'test_sql_files.TestParquet',
            #  'name': 'test_sql[nonnull-non_equi_join:test_63.sql]',
            #  'time': '11.662'}
            a = e.attrib.copy()
            module = a['classname']
            #test_line = f'{a["name"]}:{a["line"]}'
            run_time = '%ss ' % a['time']
            try:
                p = e.find('properties').find('property').attrib
                test_start = p['value']
            except:
                test_start = '?'
            failure = e.find('failure')
            failure_msg = short_failure_msg = failure.get('message')
            if len(failure_msg) > 130:
                short_failure_msg = f'{failure_msg[:60]}...'
            row = [
                f'{i} ',
                test_start,
                module,
                run_time,
                short_failure_msg,
            ]
            rows.append(row)
            a['failure_message'] = failure_msg
            a['failure_text'] = failure.text
            dicts.append(a)

        k = Dict()
        k.banner = (f'Failures for {self._path}.',)
        k.formats = lambda: chain(
            (str.rjust,),
            (str.center,),
            (str.rjust,),
            (str.ljust,),
            repeat(str.ljust),
        )
        k.output = self.ostream
        if self.no_fancy_unicode_chars:
            render_text_table(rows, **k)
        else:
            render_fancy_text_table(rows, **k)

        json_path = path.replace('.xml', '-failures.json')
        with open(json_path, 'w') as f:
            json.dump(dicts, f)
        out(f'Wrote {json_path}.')

        #text_path = path.replace('.xml', '-failures.txt')
        #with open(text_path, 'w') as f:
        #    for d in (Dict(d) for d in dicts):
        #        f.write(f'{d.file}:{d.line} ({d.name}): {d.failure_message}\n')
        #        f.write(indent(dedent(d.failure_text), prefix='    '))
        #        f.write('\n\n')
        #out(f'Wrote {text_path}.')

class ComparePytestResults(InvariantAwareCommand):
    """
    Parses two pytest-results.xml files and prints a tabular summary comparing
    test results for the given runs.
    """

    left = None
    _left = None
    class LeftArg(PathInvariant):
        _help = "path of left pytest-results.xml file"

    right = None
    _right = None
    class RightArg(PathInvariant):
        _help = "path of right pytest-results.xml file"

    no_fancy_unicode_chars = None
    class NoFancyUnicodeCharsArg(BoolInvariant):
        _help = "use normal ASCII chars instead of fancy Unicode counterparts"
        _mandatory = False
        _default = False

    include_successful_tests = None
    class IncludeSuccessfulTestsArg(BoolInvariant):
        _help = (
            "includes tests that were successful in both runs (normally, a "
            "row is only generated if a test failed in one or both runs)"
        )
        _mandatory = False
        _default = False

    def _process_results(self, path):
        from .util import Dict
        from xml.etree import ElementTree
        tree = ElementTree.parse(path)
        root = tree.getroot()
        elements = tree.findall('.//*testcase')
        results = {}
        check = '\u2713' if not self.no_fancy_unicode_chars else 'Y'
        cross = '\u2717' if not self.no_fancy_unicode_chars else 'N'
        for e in elements:
            a = Dict(e.attrib)
            a.test_line = f'{a.name}:{a.line}'
            a.test_id = f'{a.classname}.{a.test_line}'
            a.success = (e.find('failure') is None)
            a.result = check if a.success else cross
            # Some ETW screenshot tests appear to trigger this assertion.
            #assert a.test_id not in results, a.test_id
            results[a.test_id] = a
        return results

    def run(self):
        out = self._out

        from .util import (
            render_text_table,
            render_fancy_text_table,
            Dict,
        )

        from itertools import (
            chain,
            repeat,
        )

        left = self._process_results(self._left)
        right = self._process_results(self._right)

        ids = set()
        for test_id in chain(left.keys(), right.keys()):
            ids.add(test_id)

        rows = [(
            'Module',
            'Test:Line',
            'Left',
            'Right',
        )]

        for test_id in sorted(ids):
            l = left.get(test_id)
            r = right.get(test_id)
            t = l or r
            if not self.include_successful_tests:
                if l and r and l.success and r.success:
                    continue
            row = [
                t.classname,
                t.test_line,
                '' if not l else l.result,
                '' if not r else r.result,
            ]
            rows.append(row)

        k = Dict()
        k.banner = (
            'PyTest Result Comparision',
            f'{self.left} (left) vs {self.right} (right).',
        )
        k.formats = lambda: chain(
            (str.rjust,),
            (str.ljust,),
            (str.center,),
            (str.center,),
        )
        k.output = self.ostream
        if self.no_fancy_unicode_chars:
            render_text_table(rows, **k)
        else:
            render_fancy_text_table(rows, **k)



# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
