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
import sipsymboldata
import re

outputBaseDirectory = "/home/sbe/devel/git/kde/marble"
cmakelistBaseDirectory = outputBaseDirectory
pyqt4SipDir = "/home/sbe/devel/kdesvninstall/share/sip/PyQt4/"

###########################################################################
marble = toolkit.ModuleGenerator(
    module="PyKDE4.marble",
    outputDirectory=os.path.join(outputBaseDirectory,"src/bindings/python/sip"),
    docsOutputDirectory=os.path.join(outputBaseDirectory, "docs/bindings/python/html/marble"),
    mainDocs=os.path.join(outputBaseDirectory,"Mainpage.dox"),
    
    # .h file extraction
    cmakelists=[os.path.join(cmakelistBaseDirectory,"src/lib/marble/CMakeLists.txt"),
                os.path.join(cmakelistBaseDirectory,"src/lib/marble/geodata/CMakeLists.txt")],
    
    ignoreHeaders="""marble_export.h geodata_export.h TileCreatorDialog.h GeoDataCoordinates_p.h AbstractProjectionHelper.h EquirectProjection.h EquirectProjectionHelper.h MercatorProjection.h MercatorProjectionHelper.h SphericalProjection.h SphericalProjectionHelper.h MapThemeSortFilterProxyModel.h ExtDateTime.h MarbleWidgetInputHandler.h BoundingBox.h GeoDataDocument_p.h GeoDataMultiGeometry_p.h GeoDataPoint_p.h GeoDataFeature_p.h GeoDataLinearRing_p.h GeoDataLookAt_p.h GeoDataRegion_p.h GeoDataPlacemark_p.h GeoDataLineString_p.h GeoDataContainer_p.h GeoDataPolygon_p.h GeoDataGeometry_p.h GeoDataLod_p.h RoutingManager.h RoutingWidget.h global.h""".split(" "),

    #noUpdateSip=["phononnamespace.sip"],
    ignoreBases=["QSharedData"],
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros([
        (re.compile(r'MARBLE_DEPRECATED\((.*?)\);',re.DOTALL),r'\1;'),
        ]),
    preprocessorValues={"Q_WS_X11": 1, "QT_VERSION": "0x040400"},
    
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["MARBLE_EXPORT","GEODATA_EXPORT"]),
    
    # Sip generation
    sipImportDirs=[pyqt4SipDir,os.path.join(outputBaseDirectory,"sip")],
    sipImports=["QtCore/QtCoremod.sip","QtGui/QtGuimod.sip","QtWebKit/QtWebKitmod.sip","QtXml/QtXmlmod.sip"],
    
    copyrightNotice=qtkdemacros.copyrightNotice(),
    exportMacros=["MARBLE_EXPORT","GEODATA_EXPORT","KDE_EXPORT"],
    noCTSCC=["GeoPainter","ClipPainter","RenderPluginInterface"],
    
    annotationRules=[
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["parent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="ctor",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch=["pParent"],
            annotations="TransferThis"),
            
        toolkit.AnnotationRule(
            methodTypeMatch="function",
            parameterTypeMatch=["QWidget*","QObject*"],
            parameterNameMatch="parent",
            annotations="Transfer")
        ]
    )

###########################################################################
marble.run()

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

UpdateClassNamespaceList('marble',marble.docs())
print("Writing all classes index:")
toolkit.ModuleGenerator.WriteAllClasses(os.path.join(outputBaseDirectory,"docs/bindings/python/html"),nsNames,classNames)
print("Done")

