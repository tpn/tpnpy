#===============================================================================
# Imports
#===============================================================================
from __future__ import print_function
import os
import codecs

from ..util import (
    Dict,

    chdir,
    memoize,
    strip_empty_lines,
)

from os.path import basename

from ..path import (
    abspath,
    dirname,
    join_path,
)

from ..config import get_or_create_config

from .templates import *

#===============================================================================
# Globals
#===============================================================================
conf = get_or_create_config()

#===============================================================================
# Helper Methods
#===============================================================================

#===============================================================================
# Classes
#===============================================================================

class SourceFile(Dict):
    typename = None
    preprocessor_definitions = ''
    preprocessor_debug_definitions = ''

    def __init__(self, name, relative_path):
        self.name = name
        self.relative_path = relative_path
        self.instances.append(self)

    @classmethod
    def vcxproj(cls):
        if not cls.instances:
            return ''
        fmt = '    <%s Include="%s" />'
        r = [ '<ItemGroup>', ]
        r += [ fmt % (obj.typename, obj.relative_path)
                for obj in cls.instances
        ]
        r.append('  </ItemGroup>')
        return '\n'.join(r)

    @classmethod
    def vcxproj_filters(cls):
        if not cls.instances:
            return ''
        fmt = (
            '    <%s Include="%s">\n'
            '      <Filter>%s</Filter>\n'
            '    </%s>'
        )
        r = [ '<ItemGroup>', ]
        r += [
            fmt % (
                obj.typename,
                obj.relative_path,
                obj.filtername,
                obj.typename,
            ) for obj in cls.instances
        ]
        r.append('  </ItemGroup>')
        return '\n'.join(r)

    @classmethod
    def vcxproj_filterdef(cls, guid):
        if not cls.instances:
            return ''
        fmt = (
            '<Filter Include="%s">\n'
            '      <UniqueIdentifier>%s</UniqueIdentifier>\n'
            '    </Filter>'
        )
        return fmt % (cls.filtername, guid)

class CompileFile(SourceFile):
    instances = []
    typename = 'ClCompile'
    filtername = 'Source'

class ExternalIncludeFile(SourceFile):
    instances = []
    typename = 'None'
    filtername = 'External Headers'

class IncludeFile(SourceFile):
    instances = []
    typename = 'ClInclude'
    filtername = 'Headers'

class OtherFile(SourceFile):
    instances = []
    typename = 'None'
    filtername = 'Other'

class PythonFile(SourceFile):
    instances = []
    typename = 'None'
    filtername = 'Python'

class ResourceFile(SourceFile):
    instances = []
    typename = 'ResourceCompile'
    filtername = 'Resources'

class CythonFile(SourceFile):
    instances = []
    typename = 'None'
    filtername = 'Cython'

class Project:
    name = None
    # Relative to path:
    relative_src_dirs = [ 'src', ]
    # Relative to path
    pcbuild_dir = '..\\..\\PCbuild\\'
    pcbuild_prefix = ''
    compile_ext = [ '.c', '.cpp' ]
    header_ext = [ '.h', '.hpp' ]
    resource_ext = [ '.rc' ]
    other_ext = [ '.txt' ]
    cython_exts = [ '.pyx', '.pxd' ]
    sources = []
    source_files = []
    compile_defines = {}
    compile_release_defines = {}
    compile_debug_defines = {}
    resource_defines = {}
    resource_release_defines = {}
    resource_debug_defines = {}
    # Set to True to enable C++ exceptions (/EHsc)
    cpp_exceptions = None
    include_dirs = []
    exclude_dirs = []
    exclude_files = []

    @property
    def project_name(self):
        return self.name

    @property
    @memoize
    def extensions(self):
        x = {}
        for ext in self.compile_ext:
            x[ext] = CompileFile
        for ext in self.header_ext:
            x[ext] = IncludeFile
        for ext in self.resource_ext:
            x[ext] = ResourceFile
        for ext in self.other_ext:
            x[ext] = OtherFile
        for ext in self.cython_exts:
            x[ext] = CythonFile

        x['.py'] = PythonFile
        return x

    @property
    def base(self):
        return join_path(conf.src_dir, 'pyparallel', 'contrib')

    @property
    def base_relative_to_pcbuild(self):
        return '..\\contrib'

    @property
    def path(self):
        return join_path(self.base, self.name)

    @property
    def src_path(self):
        return join_path(self.path, self.relative_src_dir)

    @property
    def pcbuild_abspath(self):
        return abspath(join_path(self.path, self.pcbuild_dir))

    @property
    def vcxproj_filename(self):
        return join_path(
            self.pcbuild_abspath,
            self.project_name + '.vcxproj',
        )

    @property
    def vcxproj_filters_filename(self):
        return join_path(
            self.pcbuild_abspath,
            self.project_name + '.vcxproj.filters',
        )

    @property
    def props_filename(self):
        return join_path(
            self.pcbuild_abspath,
            self.project_name + '.props',
        )

    @property
    def props_debug_filename(self):
        return join_path(
            self.pcbuild_abspath,
            self.project_name + '_debug.props',
        )

    @property
    def dirname_macro(self):
        return '$(%s)' % self.dirname_macro_name

    @property
    def dirname_macro_name(self):
        return '%sDir' % self.name

    @property
    def dirname_macro_value(self):
        return '\\'.join((self.base_relative_to_pcbuild, basename(self.path)))

    def exclude_custom(self, root, filename):
        return False

    def load(self):
        extensions = self.extensions
        exts = extensions.keys()
        exclude_files = set(self.exclude_files)
        exclude_dirs = set(self.exclude_dirs)

        with chdir(self.path):
            for d in self.relative_src_dirs:
                for (root, dirs, files) in os.walk(d):
                    for f in files:
                        ix = f.rfind('.')
                        if ix == -1:
                            continue
                        ext = f[ix:].lower()
                        if ext not in exts:
                            continue
                        if f in exclude_files:
                            continue
                        if self.exclude_custom(root, f):
                            continue
                        cls = extensions[ext]
                        relpath = '\\'.join((self.dirname_macro, root, f))
                        source = cls(f, relpath)
                        self.sources.append(source)
                        self.source_files.append(relpath)


    def __getitem__(self, name):
        # (So we can do things like `return text % self`.)
        return getattr(self, name)

    @property
    def compiles(self):
        return CompileFile.vcxproj()

    @property
    def includes(self):
        return IncludeFile.vcxproj()

    @property
    def resources(self):
        return ResourceFile.vcxproj()

    @property
    def others(self):
        return OtherFile.vcxproj()

    @property
    def pythons(self):
        return PythonFile.vcxproj()

    @property
    def cythons(self):
        return Cythons.vcxproj()

    @property
    def vcxproj(self):
        return strip_empty_lines(vcxproj_template % self)

    @property
    def source_filterdef(self):
        return CompileFile.vcxproj_filterdef(self.source_filterdef_guid)

    @property
    def include_filterdef(self):
        return IncludeFile.vcxproj_filterdef(self.include_filterdef_guid)

    @property
    def resource_filterdef(self):
        return ResourceFile.vcxproj_filterdef(self.resource_filterdef_guid)

    @property
    def python_filterdef(self):
        return PythonFile.vcxproj_filterdef(self.python_filterdef_guid)

    @property
    def cython_filterdef(self):
        return CythonFile.vcxproj_filterdef(self.cython_filterdef_guid)

    @property
    def other_filterdef(self):
        return OtherFile.vcxproj_filterdef(self.other_filterdef_guid)

    @property
    def source_filters(self):
        return CompileFile.vcxproj_filters()

    @property
    def include_filters(self):
        return IncludeFile.vcxproj_filters()

    @property
    def resource_filters(self):
        return ResourceFile.vcxproj_filters()

    @property
    def other_filters(self):
        return OtherFile.vcxproj_filters()

    @property
    def cython_filters(self):
        return CythonFile.vcxproj_filters()

    @property
    def python_filters(self):
        return PythonFile.vcxproj_filters()

    @property
    def vcxproj_filters(self):
        return strip_empty_lines(vcxproj_filters_template % self)

    @property
    def exception_handling(self):
        if self.cpp_exceptions:
            return '\n      <ExceptionHandling>Sync</ExceptionHandling>'
        else:
            return ''

    @property
    def additional_include_dirs(self):
        if not self.include_dirs:
            return ''

        dirs = ';'.join([
            '\\'.join((self.dirname_macro, d))
                for d in self.include_dirs
        ])
        fmt = (
            '\n      '
            '<AdditionalIncludeDirectories>%s'
            '</AdditionalIncludeDirectories>'
        )
        return fmt % dirs

    def _preprocessor_defines(self, d1, d2=None):
        if not d1:
            return ''

        defines = { k: v for (k, v) in d1.items() }
        if d2:
            defines.update(d2)

        s = ';'.join('%s=%s' % i for i in defines.items())
        s += ';%(PreprocessorDefinitions)'
        fmt = '\n      <PreprocessorDefinitions>%s</PreprocessorDefinitions>\n'
        return fmt % s

    @property
    def compiles_props(self):
        return self._preprocessor_defines(self.compile_defines)

    @property
    def resources_props(self):
        return self._preprocessor_defines(self.resource_defines)

    @property
    def props(self):
        return strip_empty_lines(props_template % self)

    @property
    def compiles_debug_props(self):
        return self._preprocessor_defines(
            self.compile_defines,
            self.compile_debug_defines,
        )

    @property
    def resources_debug_props(self):
        return self._preprocessor_defines(
            self.resource_defines,
            self.resource_debug_defines,
        )

    @property
    def props_debug(self):
        return strip_empty_lines(props_debug_template % self)

    def _write(self, filename, text):
        # utf-8-sig: writes utf-8 BOM at start.
        with open(filename, 'w', encoding='utf-8-sig', newline='\r\n') as f:
            f.write(text)
        print("wrote %s" % filename)

    def write_vcxproj(self):
        self._write(self.vcxproj_filename, self.vcxproj)

    def write_vcxproj_filters(self):
        self._write(self.vcxproj_filters_filename, self.vcxproj_filters)

    def write_props(self):
        self._write(self.props_filename, self.props)

    def write_props_debug(self):
        self._write(self.props_debug_filename, self.props_debug)

    def write(self):
        self.write_vcxproj()
        self.write_vcxproj_filters()
        self.write_props()
        self.write_props_debug()

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
