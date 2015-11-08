#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#     Copyright 2009-2014 Simon Edwards <simon@simonzone.com>
#     Copyright 2015 Scott Kitterman <scott@kitterman.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import argparse
import configparser
import inspect
import kbindinggenerator.toolkit as toolkit
import kbindinggenerator.qtkde5macros as qtkde5macros
import kbindinggenerator.sipsymboldata as sipsymboldata
import os
import re

kauth = None
kitemmodels = None
kitemviews = None
karchive = None
kplotting = None
solid = None
kcoreaddons = None
sonnet = None
kguiaddons = None
kwidgetsaddons = None

def _readConfiguration(configfile):

    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(configfile)
    
    return(settings)

def _writeConfiguration(settings, configfile):
    cfgfile = open(configfile,'w')
    settings.write(cfgfile)
    cfgfile.close()

def _setSettings(settings):
    outputBaseDirectory = os.environ['HOME'] + \
        settings.get('kf5.config', 'outputBaseDirectory')
    cmakelistBaseDirectory = os.environ['HOME'] + \
        settings.get('kf5.config', 'cmakelistBaseDirectory')
    kdelibsBuildDirectory = os.environ['HOME'] + \
        settings.get('kf5.config', 'kdelibsBuildDirectory')
    cmakelistGitBaseDirectory = os.environ['HOME'] + \
        settings.get('kf5.config', 'cmakelistGitBaseDirectory')
    sipImportDir = os.environ['HOME'] + settings.get('kf5.config', 'sipImportDir')
    sipImportDirs = [ str(sipImportDir), str(outputBaseDirectory) + '/sip']
    return(outputBaseDirectory, cmakelistBaseDirectory, kdelibsBuildDirectory,
        cmakelistGitBaseDirectory, sipImportDir, sipImportDirs)

def _getConfiguration(configfile):
    settings = _readConfiguration(configfile)
    outputBaseDirectory, cmakelistBaseDirectory, kdelibsBuildDirectory, \
        cmakelistGitBaseDirectory, sipImportDir, sipImportDirs =_setSettings(settings)
    return(outputBaseDirectory, cmakelistBaseDirectory, kdelibsBuildDirectory,
        cmakelistGitBaseDirectory, sipImportDir, sipImportDirs)

def _printConfiguration(outputBaseDirectory, cmakelistBaseDirectory,
    kdelibsBuildDirectory, cmakelistGitBaseDirectory, sipImportDir,
    sipImportDirs):
    print('Current values for configuration options:')
    print('outputBaseDirectory = {0}'.format(outputBaseDirectory))
    print('cmakelistBaseDirectory = {0}'.format(cmakelistBaseDirectory))
    print('kdelibsBuildDirectory = {0}'.format(kdelibsBuildDirectory))
    print('cmakelistGitBaseDirectory = {0}'.format(cmakelistGitBaseDirectory))
    print('sipImportDir = {0}'.format(sipImportDir))
    print('sipImportDirs = {0}'.format(sipImportDirs))

def _setupAll(outputBaseDirectory, cmakelistBaseDirectory,
    kdelibsBuildDirectory, cmakelistGitBaseDirectory, sipImportDir,
    sipImportDirs):

    global kauth
    global kitemmodels
    global kitemviews
    global karchive
    global kplotting
    global solid
    global kcoreaddons
    global sonnet
    global kguiaddons
    global kwidgetsaddons
    ###########################################################################
    kauth = toolkit.ModuleGenerator(
        module="PyKDE5.kauth",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kauth"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kauth"),
        mainDocs=os.path.join(cmakelistBaseDirectory,"kauth/Mainpage.dox"),
        
        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kauth/CMakeLists.txt"),
        
        ignoreHeaders="""kauth_export.h kauth_version.h kauth.h""".split(" "),
        
        #noUpdateSip=["typedefs.sip"],
        
        # Cpp parsing    
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KAUTH_EXPORT"]),
        
        # Sip generation
        sipImportDirs=[sipImportDir],
        sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtNetwork/QtNetworkmod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KAUTH_EXPORT"],
        ignoreBases=[],
        
        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    kitemmodels = toolkit.ModuleGenerator(
        module="PyKDE5.kitemmodels",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kitemmodels"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kitemmodels"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"kitemmodels/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kitemmodels/CMakeLists.txt"),

        ignoreHeaders="""kitemmodels_export.h kitemmodels_version.h kitemmodels.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KITEMMODELS_EXPORT"]),

        # Sip generation
        sipImportDirs=[sipImportDir],
        sipImports=["QtCore/QtCoremod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KITEMMODELS_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    kitemviews = toolkit.ModuleGenerator(
        module="PyKDE5.kitemviews",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kitemviews"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kitemviews"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"kitemviews/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kitemviews/CMakeLists.txt"),

        ignoreHeaders="""kitemviews_export.h kitemviews_version.h kitemviews.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1", "KITEMVIEWS_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KITEMVIEWS_EXPORT"]),

        # Sip generation
        sipImportDirs=[sipImportDir],
        sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtWidgets/QtWidgetsmod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KITEMVIEWS_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    karchive = toolkit.ModuleGenerator(
        module="PyKDE5.karchive",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/karchive"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/karchive"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"karchive/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"karchive/CMakeLists.txt"),

        ignoreHeaders="""karchive_export.h karchive_version.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1", "KARCHIVE_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KARCHIVE_EXPORT"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KARCHIVE_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    kplotting = toolkit.ModuleGenerator(
        module="PyKDE5.kplotting",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kplotting"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kplotting"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"kplotting/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kplotting/CMakeLists.txt"),

        ignoreHeaders="""kplotting_export.h kplotting_version.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KPLOTTING_EXPORT"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip", "QtGui/QtGuimod.sip", "QtWidgets/QtWidgetsmod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KPLOTTING_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    solid = toolkit.ModuleGenerator(
        module="PyKDE5.solid",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/solid"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/solid"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"solid/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"solid/CMakeLists.txt"),

        ignoreHeaders="""solid_export.h solid_version.h kuser.h acpluggedjob.h inhibition.h inhibitionjob.h job.h power.h requeststatejob.h statesjob.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["SOLID_EXPORT", "SOLID_DEPRECATED"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["SOLID_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    kcoreaddons = toolkit.ModuleGenerator(
        module="PyKDE5.kcoreaddons",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kcoreaddons"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kcoreaddons"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"kcoreaddons/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kcoreaddons/CMakeLists.txt"),
        cmakeVariables = {"cmake_current_binary_dir": [kdelibsBuildDirectory + "/kcoreaddons"]},

        ignoreHeaders="""kcoreaddons_export.h kcoreaddons_version.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1", "KCOREADDONS_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KCOREADDONS_EXPORT"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KCOREADDONS_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    sonnet = toolkit.ModuleGenerator(
        module="PyKDE5.sonnet",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/sonnet"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/sonnet"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"sonnet/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"sonnet/CMakeLists.txt"),

        ignoreHeaders="""sonnetui_export.h sonnet_export.h sonnet_version.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["SONNETCORE_EXPORT","SONNETUI_EXPORT"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip", "QtGui/QtGuimod.sip", "QtWidgets/QtWidgetsmod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["SONNET_EXPORT","SONNETUI_EXPORT","SONNETCORE_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    kguiaddons = toolkit.ModuleGenerator(
        module="PyKDE5.kguiaddons",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kguiaddons"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kguiaddons"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"kguiaddons/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kguiaddons/CMakeLists.txt"),
        cmakeVariables = {"cmake_current_binary_dir": [kdelibsBuildDirectory + "/kguiaddons"]},

        ignoreHeaders="""kguiaddons_export.h kguiaddons_version.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KGUIADDONS_EXPORT"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip", "QtGui/QtGuimod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KGUIADDONS_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

    ###########################################################################
    kwidgetsaddons = toolkit.ModuleGenerator(
        module="PyKDE5.kwidgetsaddons",
        outputDirectory=os.path.join(outputBaseDirectory, "sip/kwidgetsaddons"),
        docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kwidgetsaddons"),
        # mainDocs=os.path.join(cmakelistBaseDirectory,"kwidgetsaddons/Mainpage.dox"),

        # .h file extraction
        cmakelists=os.path.join(cmakelistBaseDirectory,"kwidgetsaddons/CMakeLists.txt"),
        cmakeVariables = {"cmake_current_binary_dir": [kdelibsBuildDirectory + "/kwidgetsaddons"]},

        ignoreHeaders="""kwidgetsaddons_export.h kwidgetsaddons_version.h""".split(" "),

        #noUpdateSip=["typedefs.sip"],

        preprocessorValues={"KDE_NO_DEPRECATED": "1", "KWIDGETSADDONS_NO_DEPRECATED": "1"},

        # Cpp parsing
        preprocessSubstitutionMacros=qtkde5macros.QtPreprocessSubstitutionMacros(),
        macros=qtkde5macros.QtMacros(),
        bareMacros=qtkde5macros.QtBareMacros(["KWIDGETSADDONS_EXPORT"]),

        # Sip generation
        sipImportDirs=sipImportDirs,
        sipImports=["typedefs.sip", "QtCore/QtCoremod.sip", "QtWidgets/QtWidgetsmod.sip"],
        copyrightNotice=qtkde5macros.copyrightNotice(),
        exportMacros=["KWIDGETSADDONS_EXPORT"],
        ignoreBases=[],

        annotationRules=qtkde5macros.annotationRules()
        )

def updateSIP():
    global kauth
    global kitemmodels
    global kitemviews
    global karchive
    global kplotting
    global solid
    global kcoreaddons
    global sonnet
    global kguiaddons
    global kwidgetsaddons
    kauth.run()
    kitemmodels.run()
    kitemviews.run()
    karchive.run()
    kplotting.run()
    solid.run()
    kcoreaddons.run()
    sonnet.run()

    # kcodecs N/A - use Python's libraries for this functionality.
    # kwindowsystem N/A

    kguiaddons.run()
    kwidgetsaddons.run()

    # TODO
    # kconfig
    # kjs

def updateDocs():
    global kauth
    global kitemmodels
    global kitemviews
    global karchive
    global kplotting
    global solid
    global kcoreaddons
    global sonnet
    global kguiaddons
    global kwidgetsaddons
    classNames = []
    nsNames = []

    def UpdateClassNamespaceList(moduleName,sipScopes):
        nsNames.append( (moduleName,'global', 'global') )
        def ExtractClassNamespace(scope):
            for item in scope:
                if isinstance(item,sipsymboldata.SymbolData.SipClass):
                    classNames.append( (moduleName, item.fqPythonName(), item.fqPythonName()) )
                    ExtractClassNamespace(item)
                elif isinstance(item,sipsymboldata.SymbolData.Namespace):
                    nsTuple = (moduleName,item.fqPythonName(),item.fqPythonName())
                    if nsTuple not in nsNames:
                        nsNames.append( nsTuple )
                    ExtractClassNamespace(item)
        for scope in sipScopes:
            ExtractClassNamespace(scope)

    # UpdateClassNamespaceList('kauth',kauth.docs())
    UpdateClassNamespaceList('kitemmodels',kitemmodels.docs())
    UpdateClassNamespaceList('kitemviews',kitemviews.docs())
    UpdateClassNamespaceList('karchive',karchive.docs())
    UpdateClassNamespaceList('kplotting',kplotting.docs())
    UpdateClassNamespaceList('solid',solid.docs())
    UpdateClassNamespaceList('kcoreaddons',kcoreaddons.docs())
    UpdateClassNamespaceList('sonnet',sonnet.docs())
    UpdateClassNamespaceList('kguiaddons',kguiaddons.docs())
    UpdateClassNamespaceList('kwidgetsaddons',kwidgetsaddons.docs())

    print("Writing all classes index:")
    toolkit.ModuleGenerator.WriteAllClasses(os.path.join(outputBaseDirectory,"docs/html"),nsNames,classNames)
    print("Done")
    
###########################################################################
def main():
    """
    Process kf5 source to generate Python bindings.

    The current CONFIGFILE defaults are:

        [kf5.config]
        source = /source
        build = /build
        ...
        outputbasedirectory = ${kf5.config:source}/pykde5
            
    The output is a set of files in the outputbasedirectory directory.
    """
    configfile = os.path.join(os.path.dirname(__file__), 'config')
    parser = argparse.ArgumentParser(epilog = inspect.getdoc(main),
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--listopts', default=False, action='store_true', help='list stored configuration option values and exit')
    parser.add_argument('-f', '--configfile', default=configfile, action='store', help='path to alternate configuration file to use')
    parser.add_argument('-w', '--writeopt', default=[], action='append', help='change config file value using item=value syntax - add multiple times to change multiple values')
    args = parser.parse_args()
    try:
        outputBaseDirectory, cmakelistBaseDirectory, kdelibsBuildDirectory, \
            cmakelistGitBaseDirectory, sipImportDir, sipImportDirs =_getConfiguration(args.configfile)
    except configparser.NoSectionError as e:
        print('Config file error: {0}'.format(e))
        exit(1)
    if args.listopts:
        _printConfiguration(outputBaseDirectory, cmakelistBaseDirectory,
            kdelibsBuildDirectory, cmakelistGitBaseDirectory, sipImportDir,
            sipImportDirs)
        exit(0)
    if args.writeopt:
        for arg in args.writeopt:
            try:
                item, value = arg.split('=')
            except ValueError as e:
                print("Error: item and value must be separated by '='. {0}".format(e))
                exit(1)
            item = item.strip()
            value = value.strip()
            oldvalue = settings.get('kf5.config', item)
            print("Changing {0} from {1} to {2}".format(item, oldvalue, value))
            settings.set('kf5.config', item, value)
            _setSettings(settings)
            _writeConfiguration(settings, configfile)
        exit(0)
    _setupAll(outputBaseDirectory, cmakelistBaseDirectory,
        kdelibsBuildDirectory, cmakelistGitBaseDirectory, sipImportDir,
        sipImportDirs)
    #print(repr(kitemmodels.extractCmakeListsHeaders()))
    updateSIP()
    updateDocs()

if __name__=="__main__":
    main()
