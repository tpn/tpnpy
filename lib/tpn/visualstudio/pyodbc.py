#===============================================================================
# Imports
#===============================================================================
import textwrap

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
class PyOdbcProject(Project):
    name = 'pyodbc'
    version = '3.0.8'
    major = '3'
    minor = '0'
    micro = '8'
    build = '0'
    guid = '{D6C8B019-117C-455C-8EBC-1C9B6D9EC325}'
    source_filterdef_guid = '{A503B47E-D455-4806-947F-BFCA56EF0F9E}'
    include_filterdef_guid = '{28358B4E-0F4B-4728-8C08-1BAFB8C8566C}'
    other_filterdef_guid = '{37A2F692-0C97-11E5-9F3F-8863DFCA3C40}'
    python_filterdef_guid = '{37A2F692-0C97-11E5-9F3F-8863DFCA3C41}'
    cython_filterdef_guid = '{37A2F692-0C97-11E5-9F3F-8863DFCA3C42}'
    resource_filterdef_guid = '{37A2F692-0C97-11E5-9F3F-8863DFCA3C43}'

    compile_defines = {
        'PYODBC_UNICODE_WIDTH': '2',
    }

    resource_defines = {
        'PYODBC_VERSION': version,
        'PYODBC_MAJOR': major,
        'PYODBC_MINOR': minor,
        'PYODBC_MICRO': micro,
        'PYODBC_BUILD': build,
    }

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
