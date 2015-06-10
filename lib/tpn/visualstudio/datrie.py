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
class DatrieProject(Project):
    name = 'datrie'
    guid = '{A0A118A6-0EFA-11E5-B5EA-8863DFCA3C40}'
    relative_src_dirs = [ 'src', 'libdatrie\\datrie' ]
    source_filterdef_guid = '{A0A13FB6-0EFA-11E5-98F6-8863DFCA3C40}'
    include_filterdef_guid = '{A0A13FB7-0EFA-11E5-9F28-8863DFCA3C40}'
    other_filterdef_guid = '{A0A13FB8-0EFA-11E5-91E4-8863DFCA3C40}'
    python_filterdef_guid = '{A0A13FB9-0EFA-11E5-8DCA-8863DFCA3C40}'
    cython_filterdef_guid = '{A0A13FBA-0EFA-11E5-933D-8863DFCA3C40}'
    resource_filterdef_guid = '{A0A13FBB-0EFA-11E5-B693-8863DFCA3C40}'

    include_dirs = [ 'libdatrie' ]

    compile_defines = { }

    resource_defines = { }

# vim:set ts=8 sw=4 sts=4 tw=80 et                                             :
