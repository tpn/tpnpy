"""Visual Studio Helper Utils."""
#===============================================================================
# Imports
#===============================================================================
import uuid

#===============================================================================
# Globals
#===============================================================================

vcxproj_template = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup Label="ProjectConfigurations">
    <ProjectConfiguration Include="Debug|Win32">
      <Configuration>Debug</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Debug|x64">
      <Configuration>Debug</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="PGInstrument|Win32">
      <Configuration>PGInstrument</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="PGInstrument|x64">
      <Configuration>PGInstrument</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="PGUpdate|Win32">
      <Configuration>PGUpdate</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="PGUpdate|x64">
      <Configuration>PGUpdate</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|Win32">
      <Configuration>Release</Configuration>
      <Platform>Win32</Platform>
    </ProjectConfiguration>
    <ProjectConfiguration Include="Release|x64">
      <Configuration>Release</Configuration>
      <Platform>x64</Platform>
    </ProjectConfiguration>
  </ItemGroup>
  <PropertyGroup Label="Globals">
    <ProjectGuid>%(guid)s</ProjectGuid>
    <RootNamespace>%(name)s</RootNamespace>
    <Keyword>Win32Proj</Keyword>
  </PropertyGroup>
  <PropertyGroup Label="UserMacros">
    <%(dirname_macro_name)s>%(dirname_macro_value)s</%(dirname_macro_name)s>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='PGUpdate|Win32'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='PGInstrument|Win32'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='PGUpdate|x64'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='PGInstrument|x64'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
    <WholeProgramOptimization>true</WholeProgramOptimization>
  </PropertyGroup>
  <PropertyGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="Configuration">
    <ConfigurationType>DynamicLibrary</ConfigurationType>
    <CharacterSet>NotSet</CharacterSet>
  </PropertyGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />
  <ImportGroup Label="ExtensionSettings">
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='PGUpdate|Win32'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(pcbuild_prefix)spyd.props" />
    <Import Project="%(pcbuild_prefix)spgupdate.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='PGInstrument|Win32'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(pcbuild_prefix)spyd.props" />
    <Import Project="%(pcbuild_prefix)spginstrument.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(pcbuild_prefix)s%(name)s.props" />
    <Import Project="%(pcbuild_prefix)spyd.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(name)s_debug.props" />
    <Import Project="%(pcbuild_prefix)spyd_d.props" />
    <Import Project="%(pcbuild_prefix)sdebug.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='PGUpdate|x64'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(pcbuild_prefix)spyd.props" />
    <Import Project="%(pcbuild_prefix)sx64.props" />
    <Import Project="%(pcbuild_prefix)spgupdate.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='PGInstrument|x64'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(pcbuild_prefix)spyd.props" />
    <Import Project="%(pcbuild_prefix)sx64.props" />
    <Import Project="%(pcbuild_prefix)spginstrument.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(pcbuild_prefix)spyd.props" />
    <Import Project="%(pcbuild_prefix)sx64.props" />
  </ImportGroup>
  <ImportGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" Label="PropertySheets">
    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')" Label="LocalAppDataPlatform" />
    <Import Project="%(name)s.props" />
    <Import Project="%(name)s_debug.props" />
    <Import Project="%(pcbuild_prefix)spyd_d.props" />
    <Import Project="%(pcbuild_prefix)sdebug.props" />
    <Import Project="%(pcbuild_prefix)sx64.props" />
  </ImportGroup>
  <PropertyGroup Label="UserMacros" />
  <PropertyGroup>
    <_ProjectFileVersion>10.0.30319.1</_ProjectFileVersion>
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='Debug|x64'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='PGInstrument|Win32'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='PGInstrument|Win32'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='PGInstrument|Win32'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='PGInstrument|x64'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='PGInstrument|x64'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='PGInstrument|x64'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='PGUpdate|Win32'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='PGUpdate|Win32'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='PGUpdate|Win32'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='PGUpdate|x64'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='PGUpdate|x64'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='PGUpdate|x64'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='Release|Win32'" />
    <CodeAnalysisRuleSet Condition="'$(Configuration)|$(Platform)'=='Release|x64'">AllRules.ruleset</CodeAnalysisRuleSet>
    <CodeAnalysisRules Condition="'$(Configuration)|$(Platform)'=='Release|x64'" />
    <CodeAnalysisRuleAssemblies Condition="'$(Configuration)|$(Platform)'=='Release|x64'" />
  </PropertyGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|Win32'">
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Debug|x64'">
    <Midl>
      <TargetEnvironment>X64</TargetEnvironment>
    </Midl>
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|Win32'">
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='Release|x64'">
    <Midl>
      <TargetEnvironment>X64</TargetEnvironment>
    </Midl>
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='PGInstrument|Win32'">
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='PGInstrument|x64'">
    <Midl>
      <TargetEnvironment>X64</TargetEnvironment>
    </Midl>
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='PGUpdate|Win32'">
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  <ItemDefinitionGroup Condition="'$(Configuration)|$(Platform)'=='PGUpdate|x64'">
    <Midl>
      <TargetEnvironment>X64</TargetEnvironment>
    </Midl>
    <ClCompile>
      <AdditionalIncludeDirectories>%%(AdditionalIncludeDirectories)</AdditionalIncludeDirectories>%(exception_handling)s
    </ClCompile>
  </ItemDefinitionGroup>
  %(includes)s
  %(compiles)s
  %(resources)s
  %(others)s<ItemGroup>
    <ProjectReference Include="pythoncore.vcxproj">
      <Project>{cf7ac3d1-e2df-41d2-bea6-1e2556cdea26}</Project>
    </ProjectReference>
  </ItemGroup>
  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />
  <ImportGroup Label="ExtensionTargets">
  </ImportGroup>
</Project>"""

vcxproj_filters_template = """\
<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    %(source_filterdef)s
    %(include_filterdef)s
    %(resource_filterdef)s
    %(python_filterdef)s
    %(cython_filterdef)s
    %(other_filterdef)s
  </ItemGroup>
  %(source_filters)s
  %(include_filters)s
  %(resource_filters)s
  %(python_filters)s
  %(cython_filters)s
  %(other_filters)s
</Project>"""

props_template = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <_ProjectFileVersion>10.0.30319.1</_ProjectFileVersion>
  </PropertyGroup>
  <ItemDefinitionGroup>
    <ClCompile>%(compiles_props)s%(additional_include_dirs)s
    </ClCompile>
    <ResourceCompile>%(resources_props)s
    </ResourceCompile>
  </ItemDefinitionGroup>
</Project>"""

props_debug_template = """\
<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <PropertyGroup>
    <_ProjectFileVersion>10.0.30319.1</_ProjectFileVersion>
  </PropertyGroup>
  <ItemDefinitionGroup>
    <ClCompile>%(compiles_debug_props)s%(additional_include_dirs)s
    </ClCompile>
    <ResourceCompile>%(resources_debug_props)s
    </ResourceCompile>
  </ItemDefinitionGroup>
</Project>"""

guids_template = """\
    guid = '%s'
    source_filterdef_guid = '%s'
    include_filterdef_guid = '%s'
    other_filterdef_guid = '%s'
    python_filterdef_guid = '%s'
    cython_filterdef_guid = '%s'
    resource_filterdef_guid = '%s'
"""
num_guids = guids_template.count('%s')

#===============================================================================
# Helper Methods
#===============================================================================
def gen_guids():
    t = guids_template
    uuids = [
        '{%s}' % str(uuid.uuid1()).upper()
            for _ in range(0, num_guids)
    ]
    return t % tuple(uuids)

#===============================================================================
# Helper Classes
#===============================================================================


# vim:set ts=8 sw=4 sts=4 tw=0 et                                             :
