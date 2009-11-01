# -*- coding: utf-8 -*-
#     Copyright 2009 Simon Edwards <simon@simonzone.com>
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

import toolkit
import qtkdemacros
import os.path

outputBaseDirectory = "/home/sbe/devel/svn/kde/trunk/KDE/kdebindings/python/pykde4"
cmakelistBaseDirectory = "/home/sbe/devel/svn/kde/branches/KDE/4.3/kdelibs"

kdecore = toolkit.ModuleGenerator(
    module="PyKDE4.kdecore",
    outputDirectory=os.path.join(outputBaseDirectory, "sip/kdecore"),
    
    # .h file extraction
    cmakelists=os.path.join(cmakelistBaseDirectory,"kdecore/CMakeLists.txt"),
    
    ignoreHeaders="""conversion_check.h kallocator.h kdebug.h kcodecs.h kgenericfactory.h ksortablelist.h ktrader.h ktypelist.h  kmulticastsocket.h kmulticastsocketdevice.h kdecore_export.h kde_file.h ksocks.h kde_file.h ksharedptr.h klauncher_iface.h k3bufferedsocket.h  k3clientsocketbase.h  k3datagramsocket.h k3httpproxysocketdevice.h k3iobuffer.h  k3processcontroller.h  k3process.h  k3procio.h  k3resolver.h k3reverseresolver.h k3serversocket.h  k3socketaddress.h  k3socketbase.h  k3socketdevice.h  k3socks.h k3sockssocketdevice.h  k3streamsocket.h qtest_kde.h kdefakes.h kdeversion.h kauth.h""".split(" "),
    
    noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KDECORE_EXPORT","KDE_EXPORT","KIO_EXPORT","KDE_DEPRECATED"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/"],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtNetwork/QtNetworkmod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KDECORE_EXPORT","KDE_EXPORT","KIO_EXPORT"],
    ignoreBases=[],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="*",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="pParent",
            annotations="TransferThis")            
            ]
    )
    
###########################################################################
kdeui = toolkit.ModuleGenerator(
    module="PyKDE4.kdeui",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/kdeui"),
    
    # .h file extraction
    cmakelists=[
        os.path.join(cmakelistBaseDirectory,"kdeui/CMakeLists.txt")
        #os.path.join(cmakelistBaseDirectory,"kdeui/dialogs/CMakeLists.txt"),
        #os.path.join(cmakelistBaseDirectory,"kdeui/util/CMakeLists.txt"),
        #os.path.join(cmakelistBaseDirectory,"kdeui/widgets/CMakeLists.txt")
        ],
    
    ignoreHeaders="""kxerrorhandler.h  k3iconview.h  k3iconviewsearchline.h  k3listview.h  k3listviewlineedit.h k3listviewsearchline.h  netwm_p.h k3mimesourcefactory.h kdeui_export.h fixx11h.h kglobalshortcutinfo_p.h kkeyserver_mac.h kkeyserver_win.h""".split(" "),
    
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KDEUI_EXPORT","KDE_EXPORT","KDE_DEPRECATED","KDEUI_EXPORT_DEPRECATED"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtXml/QtXmlmod.sip","QtSvg/QtSvgmod.sip","kdecore/kdecoremod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KDEUI_EXPORT","KDE_EXPORT","KDEUI_EXPORT_DEPRECATED"],
    ignoreBases=["Q3GridView"],
    noCTSCC=["KWindowSystem","NETRootInfo","NETWinInfo"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer"),
            
        toolkit.PySlotRule(className="KDialogButtonBox",arg1Name="receiver",arg2Name="slot"),
        toolkit.PySlotRule(namespaceName="KStandardAction",arg1Name="recvr",arg2Name="slot")
        ]
    )

###########################################################################
kutils = toolkit.ModuleGenerator(
    module="PyKDE4.kutils",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/kutils"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"kutils/CMakeLists.txt")],
    ignoreHeaders="""kcmodulecontainer.h  kutils_export.h""".split(" "),
    
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KUTILS_EXPORT","KDE_EXPORT","KDE_DEPRECATED"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtXml/QtXmlmod.sip","kdecore/kdecoremod.sip","kdeui/kdeuimod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KUTILS_EXPORT","KDE_EXPORT"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################

#kdecore.run()
#kdeui.run()
kutils.run()
