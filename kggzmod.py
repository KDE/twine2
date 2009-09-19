#!/usr/bin/env python
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

tk = toolkit.ModuleGenerator(
    module="PyKDE4.kggzmod",
    outputDirectory="kggzmod",
    
    # .h file extraction
    cmakelists="/home/sbe/devel/svn/kde/trunk/KDE/kdegames/libkdegames/kggzmod/CMakeLists.txt",
    ignoreHeaders="kggzmod_export.h",
    
    # Cpp parsing    
    preprocessSubstitutionMacros=qtkdemacros.QtPreprocessSubstitutionMacros(),
    macros=qtkdemacros.QtMacros(),
    bareMacros=qtkdemacros.QtBareMacros(["KGGZMOD_EXPORT"]),
    
    # Sip generation
    sipImportDirs=["/usr/share/sip/PyQt4/"],
    sipImports=["QtCore/QtCoremod.sip"],
    copyrightNotice=qtkdemacros.copyrightNotice(),
    
    #annotationRules=[toolkit.AnnotationRule()]
    )

tk.run()
#print(repr(tk.extractCmakeListsHeaders()))