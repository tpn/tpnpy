#===============================================================================
# Imports
#===============================================================================
from .project import Project

#===============================================================================
# Globals
#===============================================================================

#===============================================================================
# Helper Methods
#===============================================================================

#===============================================================================
# Classes
#===============================================================================
class NumpyProject(Project):
    name = 'numpy'
    version = '1.9.2'
    major = '1'
    minor = '9'
    micro = '2'
    build = '0'
    #cpp_exceptions = True

    exclude_files = [
        'apple_sgemv_fix.c',
    ]
    relative_src_dirs = [
        'numpy',
        'build\\src.win-amd64-3.3\\numpy',
        #'build\\src.win-amd64-3.3\\numpy\\core\\src',
        #'build\\src.win-amd64-3.3\\numpy\\linalg',
        #'build\\src.win-amd64-3.3\\numpy\\fft',
        #'build\\src.win-amd64-3.3\\numpy\\random',
    ]
    relative_src_dirs = [ 'numpy' ]
    include_dirs = [
        'numpy\\core\\include',
        'build\\src.win-amd64-3.3\\numpy\\core\\include',
        'build\\src.win-amd64-3.3\\numpy\\core\\include\\numpy',
        'numpy\\core\\src\\private',
        'numpy\\core\\src',
        'numpy\\core',
        'numpy\\core\\src\\npymath',
        'numpy\\core\\src\\multiarray',
        'numpy\\core\\src\\umath',
        'numpy\\core\\src\\npysort',
        'build\\src.win-amd64-3.3\\numpy\\core\\include',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\private',
        'build\\src.win-amd64-3.3\\numpy\\core\\src',
        'build\\src.win-amd64-3.3\\numpy\\core',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\npymath',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\multiarray',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\umath',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\npysort',
    ]

    guid = '{9D966218-0FD0-11E5-B4A4-8863DFCA3C40}'
    source_filterdef_guid = '{9D966219-0FD0-11E5-A785-8863DFCA3C40}'
    include_filterdef_guid = '{9D96621A-0FD0-11E5-A2A8-8863DFCA3C40}'
    other_filterdef_guid = '{9D96621B-0FD0-11E5-A79E-8863DFCA3C40}'
    python_filterdef_guid = '{9D96621C-0FD0-11E5-9053-8863DFCA3C40}'
    cython_filterdef_guid = '{9D96621D-0FD0-11E5-B424-8863DFCA3C40}'
    resource_filterdef_guid = '{9D96621E-0FD0-11E5-BAD2-8863DFCA3C40}'

    compile_defines = {
        #'PYODBC_UNICODE_WIDTH': '2',
    }

    resource_defines = {
        'NUMPY_VERSION': version,
        'NUMPY_MAJOR': major,
        'NUMPY_MINOR': minor,
        'NUMPY_MICRO': micro,
        'NUMPY_BUILD': build,
    }

    def exclude_custom(self, root, filename):
        return (
            'f2py' in root or
            'test' in root or
            'tests' in root or
            'distutils' in root or
            'onefile' in filename or
            'wrapmodule' in filename
        )

class NumpyCoreMultiarrayProject(Project):
    project_name = 'numpy_core_multiarray'
    name = 'multiarray'
    version = '1.9.2'
    major = '1'
    minor = '9'
    micro = '2'
    build = '0'
    #cpp_exceptions = True

    exclude = [
        'apple_sgemv_fix.c',
    ]
    relative_src_dirs = [
        'numpy\\',
        'build\\src.win-amd64-3.3\\numpy',
        #'build\\src.win-amd64-3.3\\numpy\\core\\src',
        #'build\\src.win-amd64-3.3\\numpy\\linalg',
        #'build\\src.win-amd64-3.3\\numpy\\fft',
        #'build\\src.win-amd64-3.3\\numpy\\random',
    ]
    relative_src_dirs = [ 'numpy' ]
    include_dirs = [
        'numpy\\core\\include',
        'build\\src.win-amd64-3.3\\numpy\\core\\include',
        'build\\src.win-amd64-3.3\\numpy\\core\\include\\numpy',
        'numpy\\core\\src\\private',
        'numpy\\core\\src',
        'numpy\\core',
        'numpy\\core\\src\\npymath',
        'numpy\\core\\src\\multiarray',
        'numpy\\core\\src\\umath',
        'numpy\\core\\src\\npysort',
        'build\\src.win-amd64-3.3\\numpy\\core\\include',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\private',
        'build\\src.win-amd64-3.3\\numpy\\core\\src',
        'build\\src.win-amd64-3.3\\numpy\\core',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\npymath',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\multiarray',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\umath',
        'build\\src.win-amd64-3.3\\numpy\\core\\src\\npysort',
    ]

    guid = '{9D966218-0FD0-11E5-B4A4-8863DFCA3C40}'
    source_filterdef_guid = '{9D966219-0FD0-11E5-A785-8863DFCA3C40}'
    include_filterdef_guid = '{9D96621A-0FD0-11E5-A2A8-8863DFCA3C40}'
    other_filterdef_guid = '{9D96621B-0FD0-11E5-A79E-8863DFCA3C40}'
    python_filterdef_guid = '{9D96621C-0FD0-11E5-9053-8863DFCA3C40}'
    cython_filterdef_guid = '{9D96621D-0FD0-11E5-B424-8863DFCA3C40}'
    resource_filterdef_guid = '{9D96621E-0FD0-11E5-BAD2-8863DFCA3C40}'

    compile_defines = {
        #'PYODBC_UNICODE_WIDTH': '2',
    }

    resource_defines = {
        'NUMPY_VERSION': version,
        'NUMPY_MAJOR': major,
        'NUMPY_MINOR': minor,
        'NUMPY_MICRO': micro,
        'NUMPY_BUILD': build,
    }


# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
