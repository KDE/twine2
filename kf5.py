#!env python3
# -*- coding: utf-8 -*-
#     Copyright 2009-2014 Simon Edwards <simon@simonzone.com>
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

import re
import toolkit
import qtkde5macros
import os.path
import sipsymboldata
import configparser
import os

def _readConfiguration(configfile):

    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(configfile)
    
    return(settings)

configfile = 'config'
settings = _readConfiguration(configfile)

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

# Leaving pre-refactor values for now, can delete later.
#outputBaseDirectory = "/home/sbe/devel/git/kde/kdebindings/pykde5"
#cmakelistBaseDirectory = "/home/sbe/devel/git/kde/frameworks"
#kdelibsBuildDirectory = "/home/sbe/devel/git_build/kde/frameworks"
#cmakelistGitBaseDirectory = "/home/sbe/devel/git"
#sipImportDir = "/home/sbe/devel/kdesvninstall/share/sip/PyQt5"
#sipImportDirs = [sipImportDir, outputBaseDirectory+"/sip"]

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
    cmakeVariables = {"cmake_current_binary_dir": ["/home/sbe/devel/git_build/kde/frameworks/kcoreaddons"]},

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
    cmakeVariables = {"cmake_current_binary_dir": ["/home/sbe/devel/git_build/kde/frameworks/kguiaddons"]},

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
    cmakeVariables = {"cmake_current_binary_dir": ["/home/sbe/devel/git_build/kde/frameworks/kwidgetsaddons"]},

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

###########################################################################

def updateSIP():
    #kauth.run()
    kitemmodels.run()
    #kitemviews.run()
    #karchive.run()
    #kplotting.run()
    #solid.run()
    #kcoreaddons.run()
    #sonnet.run()

    # kcodecs N/A - use Python's libraries for this functionality.
    # kwindowsystem N/A

    #kguiaddons.run()
    #kwidgetsaddons.run()

    # TODO
    # kconfig
    # kjs

def updateDocs():
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
    '''UpdateClassNamespaceList('kitemviews',kitemviews.docs())
    UpdateClassNamespaceList('karchive',karchive.docs())
    UpdateClassNamespaceList('kplotting',kplotting.docs())
    UpdateClassNamespaceList('solid',solid.docs())
    UpdateClassNamespaceList('kcoreaddons',kcoreaddons.docs())
    UpdateClassNamespaceList('sonnet',sonnet.docs())
    UpdateClassNamespaceList('kguiaddons',kguiaddons.docs())
    UpdateClassNamespaceList('kwidgetsaddons',kwidgetsaddons.docs())'''

    print("Writing all classes index:")
    toolkit.ModuleGenerator.WriteAllClasses(os.path.join(outputBaseDirectory,"docs/html"),nsNames,classNames)
    print("Done")
    
def main():
    #print(repr(kitemmodels.extractCmakeListsHeaders()))
    updateSIP()
    updateDocs()

if __name__=="__main__":
    main()
