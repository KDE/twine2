#!env python
#     Copyright 2008 Simon Edwards <simon@simonzone.com>
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

import cmakelexer
import re
import os.path
import glob

def ExtractInstallFiles(filename=None,input=None):
    variables = {}
    install_list = []

    if filename is not None:
        variables['cmake_current_source_dir'] = [os.path.dirname(filename)]

    ExtractInstallFilesWithContext(variables, install_list, filename,input)
#    print(repr(variables))
#    print(repr(install_list))
    return install_list

def ExtractInstallFilesWithContext(variables, install_list, filename=None, input=None, fileprefix=""):
    lexer = cmakelexer.CMakeLexer()
    if input:
        lexer.input(input)
    elif filename:
        fhandle = open(filename)
        lexer.input(fhandle.read())
        fhandle.close()
        
    command_list = FetchCommands(lexer)
    for command,args in command_list:
        command = command.lower()

        if command=="set":
            variables[args[0].lower()] = ExpandArgs(variables, args[1:], filename)

        elif command=="install":
            install_args = ExpandArgs(variables, args, filename)
            install_list.extend( [os.path.join(fileprefix,x) for x in install_args if x.endswith('.h')] )

        elif command=="include":
            if filename is not None:
                command_args = ExpandArgs(variables, args, filename)
                
                this_dir = os.path.dirname(filename)
                for arg in command_args:
                    if len(arg.strip())!=0:
                        include_filename = os.path.join(this_dir,arg)
                        if os.path.exists(include_filename):
                            ExtractInstallFilesWithContext(variables, install_list, include_filename)

        elif command=="add_subdirectory":
            if filename is not None:
                command_args = ExpandArgs(variables, args, filename)

                this_dir = os.path.dirname(filename)
                for arg in command_args:
                    if len(arg.strip())!=0:
                        include_filename = os.path.join(this_dir,arg,"CMakeLists.txt")
                        if os.path.exists(include_filename):
                            ExtractInstallFilesWithContext(variables, install_list, include_filename, fileprefix=os.path.join(fileprefix,arg))

        elif command=="file":
            # This is just a basic cmake FILE() implementation. It just does GLOB.
            command_args = ExpandArgs(variables, args, filename)
            varname = None
            result = None
            try:
                it = iter(command_args)
                arg = it.next()
                if arg.lower()=='glob' and filename is not None:
                    arg = it.next()
                    varname = arg
                    arg = it.next()

                    relative_dir = os.path.dirname(filename)
                    if arg.lower()=='relative':
                        arg = it.next()
                        relative_dir = arg
                        arg = it.next()
                    if not relative_dir.endswith('/'):
                        relative_dir += '/'
                        
                    result = []
                    current_dir = variables['cmake_current_source_dir'][0]
                    while True:
                        for x in glob.iglob(os.path.join(current_dir, arg)):
                            if x.startswith(relative_dir):
                                x = x[len(relative_dir):]
                            result.append(x)
                        arg = it.next()

            except StopIteration:
                if varname is not None and result is not None:
                    variables[varname.lower()] = result

def ExpandArgs(variables, args, filename=None):
    rex  = re.compile(r'(\$\{[^\}]+\})')
    fixed_args = []
    for arg in args:
        fixed_parts = []
        parts = rex.split(arg)
        for part in parts:
            if part.startswith("${"):
                name = part[2:-1].lower()
                if name in variables:
                    value = variables[name]
                    if len(value)==1:
                        fixed_parts.append(variables[name][0])
                    else:
                        fixed_args.extend(value)
                else:
                    print("Undefined cmake variable '" + name + "' in " + filename)
            else:
                fixed_parts.append(part)
        fixed_args.append(''.join(fixed_parts))
        
    return fixed_args
    
def FetchCommands(lexer):
    topmode = True
    command_list = []
    command = None
    args = []
    
    tok = lexer.token()
    while 1:
        if not tok:
            if command:
                command_list.append( (command,args) )
            break   # No more input
        if topmode:
            if tok.type=="COMMAND":
                command = tok.value
                topmode = False
            else:
                print("Fail")
                # Fail
                
            tok = lexer.token()
        else:
            # Grab arguments
            if tok.type=="COMMAND":
                if command:
                    command_list.append( (command,args) )
                command = None
                args = []
            
                topmode = True
                continue
            args.append(tok.value)
            tok = lexer.token()
    return command_list
        
if __name__=="__main__":
    #print("Testing")
    #lexer = cmakelexer.CMakeLexer()

    print(ExtractInstallFiles(filename="/home/sbe/devel/svn/kde/trunk/KDE/kdeedu/marble/src/lib/CMakeLists.txt"))

def foo():
    ExtractInstallFiles(input="""
find_package(KDE4 REQUIRED)
include (KDE4Defaults)

include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${KDEBASE_WORKSPACE_SOURCE_DIR}/libs ${CMAKE_CURRENT_SOURCE_DIR}/.. ${KDE4_INCLUDES} ${OPENGL_INCLUDE_DIR})

add_subdirectory(tests)
add_definitions(-DKDE_DEFAULT_DEBUG_AREA=1209)

########### next target ###############

set(plasmagik_SRCS
    packagemetadata.cpp
    packagestructure.cpp
    package.cpp
    )

set(plasma_LIB_SRCS
    ${plasmagik_SRCS}
    abstractrunner.cpp
    animationdriver.cpp
    animator.cpp
    applet.cpp
    appletbrowser.cpp
    appletbrowser/customdragtreeview.cpp
    appletbrowser/kcategorizeditemsview.cpp
    appletbrowser/kcategorizeditemsviewdelegate.cpp
    appletbrowser/kcategorizeditemsviewmodels.cpp
    appletbrowser/openwidgetassistant.cpp
    appletbrowser/plasmaappletitemmodel.cpp
    configxml.cpp
    containment.cpp
    corona.cpp
    datacontainer.cpp
    dataengine.cpp
    dataenginemanager.cpp
    delegate.cpp
    dialog.cpp
    extender.cpp
    extenderitem.cpp
    paintutils.cpp
    panelsvg.cpp
    plasma.cpp
    popupapplet.cpp
    private/applethandle.cpp
    private/datacontainer_p.cpp
    private/desktoptoolbox.cpp
    private/nativetabbar.cpp
    private/packages.cpp
    private/paneltoolbox.cpp
    private/toolbox.cpp
    private/tooltip.cpp
    querymatch.cpp
    runnercontext.cpp
    runnermanager.cpp
    scripting/appletscript.cpp
    scripting/dataenginescript.cpp
    scripting/runnerscript.cpp
    scripting/scriptengine.cpp
    service.cpp
    servicejob.cpp
    svg.cpp
    theme.cpp
    tooltipmanager.cpp
    uiloader.cpp
    version.cpp
    view.cpp
    wallpaper.cpp
    widgets/checkbox.cpp
    widgets/combobox.cpp
    widgets/flash.cpp
    widgets/frame.cpp
    widgets/groupbox.cpp
    widgets/icon.cpp
    widgets/label.cpp
    widgets/lineedit.cpp
    widgets/meter.cpp
    widgets/pushbutton.cpp
    widgets/radiobutton.cpp
    widgets/signalplotter.cpp
    widgets/slider.cpp
    widgets/tabbar.cpp
    widgets/textedit.cpp
    widgets/webcontent.cpp
)

kde4_add_ui_files (
    plasma_LIB_SRCS
    appletbrowser/kcategorizeditemsviewbase.ui
)

if(QT_QTOPENGL_FOUND AND OPENGL_FOUND)
MESSAGE(STATUS "Adding support for OpenGL applets to libplasma")
set(plasma_LIB_SRCS
    ${plasma_LIB_SRCS}
    glapplet.cpp)
endif(QT_QTOPENGL_FOUND AND OPENGL_FOUND)

kde4_add_library(plasma SHARED ${plasma_LIB_SRCS})

target_link_libraries(plasma ${KDE4_KIO_LIBS} ${KDE4_KFILE_LIBS} ${KDE4_KNEWSTUFF2_LIBS}
                             ${QT_QTUITOOLS_LIBRARY} ${QT_QTWEBKIT_LIBRARY}
                             ${KDE4_THREADWEAVER_LIBRARIES} ${KDE4_SOLID_LIBS} ${X11_LIBRARIES})

if(QT_QTOPENGL_FOUND AND OPENGL_FOUND)
    target_link_libraries(plasma ${QT_QTOPENGL_LIBRARY} ${OPENGL_gl_LIBRARY})
endif(QT_QTOPENGL_FOUND AND OPENGL_FOUND)

set_target_properties(plasma PROPERTIES
                             VERSION 3.0.0
                             SOVERSION 3
                             ${KDE4_DISABLE_PROPERTY_}LINK_INTERFACE_LIBRARIES  "${KDE4_KDEUI_LIBS}"
                      )

install(TARGETS plasma ${INSTALL_TARGETS_DEFAULT_ARGS})


########### install files ###############

set(plasmagik_HEADERS
    packagemetadata.h
    packagestructure.h
    package.h
    )

install(FILES ${plasmagik_HEADERS} DESTINATION ${INCLUDE_INSTALL_DIR}/plasma/ COMPONENT Devel)

set(plasma_LIB_INCLUDES
    abstractrunner.h
    animationdriver.h
    animator.h
    applet.h
    appletbrowser.h
    configxml.h
    containment.h
    corona.h
    datacontainer.h
    dataengine.h
    dataenginemanager.h
    delegate.h
    dialog.h
    extender.h
    extenderitem.h
    paintutils.h
    panelsvg.h
    plasma.h
    plasma_export.h
    popupapplet.h
    querymatch.h
    runnercontext.h
    runnermanager.h
    service.h
    servicejob.h
    svg.h
    theme.h
    tooltipmanager.h
    uiloader.h
    tooltipmanager.h
    version.h
    view.h
    wallpaper.h)

if(QT_QTOPENGL_FOUND AND OPENGL_FOUND)
set(plasma_LIB_INCLUDES
    ${plasma_LIB_INCLUDES}
    glapplet.h)
endif(QT_QTOPENGL_FOUND AND OPENGL_FOUND)

install(FILES
        ${plasma_LIB_INCLUDES}
        DESTINATION ${INCLUDE_INSTALL_DIR}/plasma COMPONENT Devel)

install(FILES
    widgets/checkbox.h
    widgets/combobox.h
    widgets/flash.h
    widgets/frame.h
    widgets/groupbox.h
    widgets/icon.h
    widgets/label.h
    widgets/lineedit.h
    widgets/meter.h
    widgets/pushbutton.h
    widgets/radiobutton.h
    widgets/signalplotter.h
    widgets/slider.h
    widgets/tabbar.h
    widgets/textedit.h
    widgets/webcontent.h
    DESTINATION ${INCLUDE_INSTALL_DIR}/plasma/widgets COMPONENT Devel)

install(FILES
    scripting/appletscript.h
    scripting/dataenginescript.h
    scripting/runnerscript.h
    scripting/scriptengine.h
    DESTINATION ${INCLUDE_INSTALL_DIR}/plasma/scripting COMPONENT Devel)


install(FILES
includes/AbstractRunner
includes/AnimationDriver
includes/Animator
includes/Applet
includes/AppletBrowser
includes/AppletScript
includes/CheckBox
includes/ComboBox
includes/ConfigXml
includes/Containment
includes/Corona
includes/DataContainer
includes/DataEngine
includes/DataEngineManager
includes/DataEngineScript
includes/Delegate
includes/Dialog
includes/Extender
includes/ExtenderItem
includes/Flash
includes/GroupBox
includes/Icon
includes/Label
includes/LineEdit
includes/Meter
includes/Package
includes/PackageMetadata
includes/PackageStructure
includes/PaintUtils
includes/PanelSvg
includes/Plasma
includes/PopupApplet
includes/PushButton
includes/QueryMatch
includes/RadioButton
includes/RunnerContext
includes/RunnerManager
includes/RunnerScript
includes/ScriptEngine
includes/Service
includes/ServiceJob
includes/SignalPlotter
includes/Slider
includes/Svg
includes/TabBar
includes/TextEdit
includes/ToolTipManager
includes/Theme
includes/UiLoader
includes/View
includes/Version
includes/Wallpaper
includes/WebContent
DESTINATION ${INCLUDE_INSTALL_DIR}/KDE/Plasma COMPONENT Devel)

if(QT_QTOPENGL_FOUND AND OPENGL_FOUND)
   install(FILES
      includes/GLApplet
      DESTINATION ${INCLUDE_INSTALL_DIR}/KDE/Plasma COMPONENT Devel)
endif(QT_QTOPENGL_FOUND AND OPENGL_FOUND)

install(FILES
   servicetypes/plasma-animator.desktop
   servicetypes/plasma-applet.desktop
   servicetypes/plasma-containment.desktop
   servicetypes/plasma-dataengine.desktop
   servicetypes/plasma-packagestructure.desktop
   servicetypes/plasma-runner.desktop
   servicetypes/plasma-scriptengine.desktop
   servicetypes/plasma-wallpaper.desktop
   DESTINATION ${SERVICETYPES_INSTALL_DIR})

install(FILES scripting/plasmoids.knsrc DESTINATION  ${CONFIG_INSTALL_DIR})   
""")
    # Tokenize
    
    #while 1:
    #    tok = lexer.token()
    #    if not tok: break      # No more input
    #    print tok
    
    #while 1:
    #    tok = cmakelexer.lex.token()
    #    if not tok: break      # No more input
    #    print tok
    
