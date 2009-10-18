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

kdecore = toolkit.ModuleGenerator(
    module="PyKDE4.kdecore",
    outputDirectory="/home/sbe/devel/svn/kde/trunk/KDE/kdebindings/python/pykde4/sip/kdecore",
    
    # .h file extraction
    #cmakelists="/home/sbe/devel/svn/kde/trunk/KDE/kdelibs/kdecore/CMakeLists.txt",
    cmakelists="/home/sbe/devel/svn/kde/branches/KDE/4.3/kdelibs/kdecore/CMakeLists.txt",
    
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

kdecore.run()
