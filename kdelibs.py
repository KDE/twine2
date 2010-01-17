# -*- coding: utf-8 -*-
#     Copyright 2009-2010 Simon Edwards <simon@simonzone.com>
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
import sipsymboldata

#branch = "trunk/KDE"
branch = "branches/KDE/4.4"
outputBaseDirectory = "/home/sbe/devel/svn/kde/"+branch+"/kdebindings/python/pykde4"
#cmakelistBaseDirectory = "/home/sbe/devel/svn/kde/branches/KDE/4.3/kdelibs"
cmakelistBaseDirectory = "/home/sbe/devel/svn/kde/"+branch+"/kdelibs"
cmakelistSupportBaseDirectory = "/home/sbe/devel/svn/kde/trunk/kdesupport"
cmakelistPimlibsBaseDirectory = "/home/sbe/devel/svn/kde/"+branch+"/kdepimlibs"

###########################################################################
kdecore = toolkit.ModuleGenerator(
    module="PyKDE4.kdecore",
    outputDirectory=os.path.join(outputBaseDirectory, "sip/kdecore"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kdecore"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"kdecore/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=os.path.join(cmakelistBaseDirectory,"kdecore/CMakeLists.txt"),
    
    ignoreHeaders="""conversion_check.h kallocator.h kdebug.h kcodecs.h kgenericfactory.h ksortablelist.h ktrader.h ktypelist.h  kmulticastsocket.h kmulticastsocketdevice.h kdecore_export.h kde_file.h ksocks.h kde_file.h ksharedptr.h klauncher_iface.h k3bufferedsocket.h  k3clientsocketbase.h  k3datagramsocket.h k3httpproxysocketdevice.h k3iobuffer.h  k3processcontroller.h  k3process.h  k3procio.h  k3resolver.h k3reverseresolver.h k3serversocket.h  k3socketaddress.h  k3socketbase.h  k3socketdevice.h  k3socks.h k3sockssocketdevice.h  k3streamsocket.h qtest_kde.h kdefakes.h kdeversion.h kauth.h ktypelistutils.h""".split(" "),
    
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
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kdeui"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"kdeui/Mainpage.dox"),
    
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
kio = toolkit.ModuleGenerator(
    module="PyKDE4.kio",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/kio"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kio"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"kio/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[
        os.path.join(cmakelistBaseDirectory,"kio/CMakeLists.txt"),
        os.path.join(cmakelistBaseDirectory,"kfile/CMakeLists.txt")
        ],
    
    ignoreHeaders="""http_slave_defaults.h ioslave_defaults.h kmimetyperesolver.h k3mimetyperesolver.h kfiledetailview.h kfileiconview.h kfiletreeview.h kfiletreeviewitem.h ksslpemcallback.h kpropsdialog.h kio_export.h kdirnotify.h k3filedetailview.h  k3fileiconview.h k3filetreeview.h  k3filetreeviewitem.h  k3mimetyperesolver.h kfiletreebranch.h  kfile_export.h kurlbar.h""".split(" "),
    
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1,"Q_OS_UNIX": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KIO_EXPORT","KFILE_EXPORT","KIO_EXPORT_DEPRECATED","KDE_NO_EXPORT",
                    "KDE_EXPORT","KDE_DEPRECATED","","KDEUI_EXPORT_DEPRECATED","KIO_CONNECTION_EXPORT"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtXml/QtXmlmod.sip","kdecore/kdecoremod.sip","kdeui/kdeuimod.sip","solid/solidmod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KIO_EXPORT","KFILE_EXPORT","KDE_EXPORT","KDEUI_EXPORT_DEPRECATED","KIO_CONNECTION_EXPORT","KIO_EXPORT_DEPRECATED"],
    #ignoreBases=["Q3GridView"],
    noCTSCC=["KonqBookmarkContextMenu","KImportedBookmarkMenu","KBookmark","KBookmarkGroup"],
    
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
kutils = toolkit.ModuleGenerator(
    module="PyKDE4.kutils",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/kutils"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kutils"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"kutils/Mainpage.dox"),
    
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
solid = toolkit.ModuleGenerator(
    module="PyKDE4.solid",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/solid"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/solid"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"solid/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"solid/solid/CMakeLists.txt")],
    
    ignoreHeaders="""solid_export.h""".split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["SOLID_EXPORT","KDE_EXPORT","KDE_DEPRECATED"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","kdecore/kdecoremod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["SOLID_EXPORT","KDE_EXPORT"],
    
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
kparts = toolkit.ModuleGenerator(
    module="PyKDE4.kparts",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/kparts"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/kparts"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"kparts/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"kparts/CMakeLists.txt")],
    
    ignoreHeaders="""componentfactory.h genericfactory.h kparts_export.h""".split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KPARTS_EXPORT","KDE_EXPORT","KDE_DEPRECATED"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtXml/QtXmlmod.sip","kdecore/kdecoremod.sip","kdeui/kdeuimod.sip","kio/kiomod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KPARTS_EXPORT","KDE_EXPORT"],
    noCTSCC=["GenericFactoryBase"],
    
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
plasma = toolkit.ModuleGenerator(
    module="PyKDE4.plasma",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/plasma"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/plasma"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"plasma/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"plasma/CMakeLists.txt")],
    ignoreHeaders="""plasma_export.h credentials.h """.split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["PLASMA_EXPORT","PLASMA_EXPORT_DEPRECATED","KDE_EXPORT",
            "KDE_DEPRECATED","Q_INVOKABLE"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=[
        "QtCore/QtCoremod.sip",
        "QtGui/QtGuimod.sip",
        "QtNetwork/QtNetworkmod.sip",
        "QtSvg/QtSvgmod.sip",
        "QtWebKit/QtWebKitmod.sip",
        "QtXml/QtXmlmod.sip",
        "kdecore/kdecoremod.sip",
        "kdeui/kdeuimod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["PLASMA_EXPORT","PLASMA_EXPORT_DEPRECATED","KDE_EXPORT"],
    #noCTSCC=["GenericFactoryBase"],
    ignoreBases=["QSharedData","KShared","QList<KUrl>"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*","QGraphicsWidget*"],
            parameterNameMatch=["parent","pParent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*","QGraphicsWidget*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
khtml = toolkit.ModuleGenerator(
    module="PyKDE4.khtml",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/khtml"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/khtml"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"khtml/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"khtml/CMakeLists.txt"),
        #os.path.join(cmakelistBaseDirectory,"khtml/dom/CMakeLists.txt")
        ],
    
    ignoreHeaders="""khtmldefaults.h dom_core.h dom_html.h khtml_events.h khtml_export.h""".split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KHTML_EXPORT","KDE_EXPORT","KDE_DEPRECATED","Q_INVOKABLE"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=[
        "QtCore/QtCoremod.sip",
        "QtGui/QtGuimod.sip",
        "QtXml/QtXmlmod.sip",
        "kdecore/kdecoremod.sip",
        "kdeui/kdeuimod.sip",
        "kio/kiomod.sip",
        "kutils/kutilsmod.sip",
        "kparts/kpartsmod.sip",],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KHTML_EXPORT","KDE_EXPORT"],
    noCTSCC=["CSSRule","CSSCharsetRule","CSSFontFaceRule","CSSImportRule","CSSMediaRule","CSSPageRule",
        "CSSStyleRule","CSSUnknownRule","CSSStyleSheet","CSSPrimitiveValue","CSSValueList"],
    ignoreBases=["khtml::KHTMLWidget"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
def KNewStuffMapper(mod,headerName):
    print("KNewStuffMapper: "+headerName)
    filename = os.path.basename(headerName)
    if filename.endswith(".h"):
        sipName = filename[:-2]+".sip"
        if "knewstuff3" in headerName:
            return "knewstuff3_"+sipName
        else:
            return sipName
    return filename

def KNewStuffCppHeaderMapper(mod,filename):
    if "knewstuff3" in filename:
        return "knewstuff3/" + os.path.basename(filename)
    else:
        return os.path.basename(filename)

knewstuff = toolkit.ModuleGenerator(
    module="PyKDE4.knewstuff",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/knewstuff"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/knewstuff"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"knewstuff/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"knewstuff/CMakeLists.txt"),
        os.path.join(cmakelistBaseDirectory,"knewstuff/knewstuff2/CMakeLists.txt"),
        os.path.join(cmakelistBaseDirectory,"knewstuff/knewstuff3/CMakeLists.txt")],
    
    ignoreHeaders="""knewstuff_export.h""".split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KNEWSTUFF_EXPORT","KNEWSTUFF_EXPORT_DEPRECATED","KDE_EXPORT","KDE_DEPRECATED","Q_INVOKABLE"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=[
        "QtCore/QtCoremod.sip",
        "QtGui/QtGuimod.sip",
        "QtXml/QtXmlmod.sip",
        "kdecore/kdecoremod.sip",
        "kdeui/kdeuimod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KNEWSTUFF_EXPORT","KNEWSTUFF_EXPORT_DEPRECATED","KDE_EXPORT"],
    #noCTSCC=[],
    #ignoreBases=["khtml::KHTMLWidget"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ],
    filenameMappingFunction=KNewStuffMapper,
    cppHeaderMappingFunction=KNewStuffCppHeaderMapper
    )
    
###########################################################################
dnssd = toolkit.ModuleGenerator(
    module="PyKDE4.dnssd",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/dnssd"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/dnssd"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"dnssd/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"dnssd/CMakeLists.txt")],
    
    ignoreHeaders="""dnssd_export.h settings.h""".split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KDNSSD_EXPORT","KDE_EXPORT","KDE_DEPRECATED","Q_INVOKABLE"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=[
        "QtCore/QtCoremod.sip",
        "QtGui/QtGuimod.sip",
        "kdecore/kdecoremod.sip",
        "kdeui/kdeuimod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["KDNSSD_EXPORT","KDE_EXPORT"],
    #noCTSCC=[],
    #ignoreBases=["khtml::KHTMLWidget"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
nepomuk = toolkit.ModuleGenerator(
    module="PyKDE4.nepomuk",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/nepomuk"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/nepomuk"),
    mainDocs=os.path.join(cmakelistBaseDirectory,"nepomuk/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"nepomuk/CMakeLists.txt"),
        os.path.join(cmakelistBaseDirectory,"nepomuk/core/CMakeLists.txt"),
        os.path.join(cmakelistBaseDirectory,"nepomuk/core/ontology/CMakeLists.txt"),
        os.path.join(cmakelistBaseDirectory,"nepomuk/core/ui/CMakeLists.txt")],
    
    ignoreHeaders="""nepomuk_export.h ontologyloader.h desktopontologyloader.h fileontologyloader.h ontologymanager.h nepomukontologyloader.h""".split(" "),
    #noUpdateSip=["typedefs.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["NEPOMUK_EXPORT","KDE_EXPORT","KDE_DEPRECATED","Q_INVOKABLE"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=[
        "QtCore/QtCoremod.sip",
        "kdecore/kdecoremod.sip",
        "soprano/sopranomod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["NEPOMUK_EXPORT","KDE_EXPORT"],
    #noCTSCC=[],
    #ignoreBases=["khtml::KHTMLWidget"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
soprano = toolkit.ModuleGenerator(
    module="PyKDE4.soprano",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/soprano"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/soprano"),
    mainDocs=os.path.join(cmakelistSupportBaseDirectory,"soprano/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistSupportBaseDirectory,"soprano/CMakeLists.txt"),
            os.path.join(cmakelistSupportBaseDirectory,"soprano/soprano/CMakeLists.txt"),
            os.path.join(cmakelistSupportBaseDirectory,"soprano/server/CMakeLists.txt"),
            #os.path.join(cmakelistSupportBaseDirectory,"soprano/server/sparql/CMakeLists.txt"),
            os.path.join(cmakelistSupportBaseDirectory,"soprano/server/dbus/CMakeLists.txt")],
    
    ignoreHeaders="""soprano_export.h sopranomacros.h soprano.h vocabulary.h iterator.h version.h iteratorbackend.h""".split(" "),
    #noUpdateSip=["iterator.sip"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1, "USING_SOPRANO_NRLMODEL_UNSTABLE_API":1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["SOPRANO_EXPORT","SOPRANO_CLIENT_EXPORT","SOPRANO_SERVER_EXPORT",
                    "USING_SOPRANO_NRLMODEL_UNSTABLE_API","KDE_EXPORT","KDE_DEPRECATED","Q_INVOKABLE",
                    "SOPRANO_DEPRECATED"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtNetwork/QtNetworkmod.sip"],
    
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["SOPRANO_EXPORT","SOPRANO_CLIENT_EXPORT","SOPRANO_SERVER_EXPORT","KDE_EXPORT"],
    #noCTSCC=[],
    ignoreBases=["IteratorBackend<BindingSet>","Iterator<Node>","Iterator<BindingSet>","Iterator<Statement>"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
akonadi = toolkit.ModuleGenerator(
    module="PyKDE4.akonadi",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/akonadi"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/akonadi"),
    mainDocs=os.path.join(cmakelistPimlibsBaseDirectory,"akonadi/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistPimlibsBaseDirectory,"akonadi/CMakeLists.txt"),
        os.path.join(cmakelistPimlibsBaseDirectory,"akonadi/kmime/CMakeLists.txt"),
        os.path.join(cmakelistPimlibsBaseDirectory,"akonadi/kabc/CMakeLists.txt")],
    
    ignoreHeaders="""akonadi_export.h akonadi-kmime_export.h akonadi-kabc_export.h itempayloadinternals_p.h collectionpathresolver_p.h qtest_akonadi.h exception.h contactparts.h""".split(" "),
    #resourcebase.h agentbase.h 
    #noUpdateSip=["iterator.sip"],
    ignoreBases=["QDBusContext"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(["AKONADI_DECLARE_PRIVATE"]),
    bareMacros=qtkdemacros.QtBareMacros(["AKONADI_EXPORT","KDE_EXPORT","KDE_DEPRECATED","Q_INVOKABLE",
                    "AKONADI_KABC_EXPORT","AKONADI_KMIME_EXPORT"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","kdeui/kdeuimod.sip","kdecore/kdecoremod.sip","kio/kiomod.sip"],
    
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["AKONADI_EXPORT","AKONADI_KABC_EXPORT","AKONADI_KMIME_EXPORT","KDE_EXPORT"],
    noCTSCC=["Collection","Entity","Item"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
polkitqt = toolkit.ModuleGenerator(
    module="PyKDE4.polkitqt",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/polkitqt"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/polkitqt"),
    mainDocs=os.path.join(cmakelistSupportBaseDirectory,"polkit-qt/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistSupportBaseDirectory,"polkit-qt/CMakeLists.txt")],
    
    ignoreHeaders="""export.h polkitqtversion.h""".split(" "),
    #resourcebase.h agentbase.h 
    #noUpdateSip=["iterator.sip"],
    #ignoreBases=["QDBusContext"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["POLKIT_QT_EXPORT"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip"],
    
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["POLKIT_QT_EXPORT","KDE_EXPORT"],
    #noCTSCC=[],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
phonon = toolkit.ModuleGenerator(
    module="PyKDE4.phonon",
    outputDirectory=os.path.join(outputBaseDirectory,"sip/phonon"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/html/phonon"),
    mainDocs=os.path.join(cmakelistSupportBaseDirectory,"phonon/Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistSupportBaseDirectory,"phonon/phonon/CMakeLists.txt")],
    
    ignoreHeaders="""phonondefs.h  phonon_export.h export.h kaudiodevicelist_export.h phononnamespace.h addoninterface.h volumefaderinterface.h backendinterface.h effectinterface.h mediaobjectinterface.h platformplugin.h audiodataoutputinterface.h audiooutputinterface.h""".split(" "),

    noUpdateSip=["phononnamespace.sip"],
    ignoreBases=["QSharedData"],
    #ignoreBases=["AbstractAudioOutput", "Phonon::AbstractAudioOutput", "QSharedData", "AbstractVideoOutput",
    #                "Phonon::AbstractVideoOutput"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    preprocessorValues={"Q_WS_X11": 1, "QT_VERSION": "0x040400", "_MSC_VER": 0},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["PHONON_EXPORT","PHONONEXPERIMENTAL_EXPORT",
        "KAUDIODEVICELIST_EXPORT"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/",os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtXml/QtXmlmod.sip","solid/solidmod.sip"],
    
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["PHONON_EXPORT","KDE_EXPORT","PHONONEXPERIMENTAL_EXPORT","KAUDIODEVICELIST_EXPORT"],
    #noCTSCC=[],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
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
#plasma.run()
#kdeui.run()
#kio.run()
#kutils.run()
#solid.run()
#kparts.run()
#khtml.run()
#knewstuff.run()
#dnssd.run()
#nepomuk.run()
#soprano.run()
#akonadi.run()
#polkitqt.run()
#phonon.run()


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

#UpdateClassNamespaceList('kdecore',kdecore.docs())
"""UpdateClassNamespaceList('plasma',plasma.docs())
UpdateClassNamespaceList('kdeui',kdeui.docs())
UpdateClassNamespaceList('kio',kio.docs())
UpdateClassNamespaceList('kutils',kutils.docs())
UpdateClassNamespaceList('solid',solid.docs())
UpdateClassNamespaceList('kparts',kparts.docs())
UpdateClassNamespaceList('khtml',khtml.docs())
UpdateClassNamespaceList('knewstuff',knewstuff.docs())
UpdateClassNamespaceList('dnssd',dnssd.docs())
UpdateClassNamespaceList('nepomuk',nepomuk.docs())
UpdateClassNamespaceList('soprano',soprano.docs())
UpdateClassNamespaceList('akonadi',akonadi.docs())
UpdateClassNamespaceList('polkitqt',polkitqt.docs())
UpdateClassNamespaceList('phonon',phonon.docs())

print("Writing all classes index:")
toolkit.ModuleGenerator.WriteAllClasses(os.path.join(outputBaseDirectory,"new_docs/html"),nsNames,classNames)
print("Done")

"""