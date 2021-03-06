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

import re

__QtBareMacros = ["Q_OBJECT", "Q_GADGET", "Q_OBJECT_CHECK", "K_DCOP", "Q_CORE_EXPORT", "Q_INVOKABLE",
                    "QT_BEGIN_HEADER","QT_BEGIN_NAMESPACE", "QT_END_HEADER","QT_END_NAMESPACE"]

def QtBareMacros(extraMacros=[]):
    macros = __QtBareMacros[:]
    macros.extend(extraMacros)
    return macros
    
__QtMacros = [
        "Q_ENUMS", "Q_PROPERTY", "Q_OVERRIDE", "Q_SETS", "Q_CLASSINFO",\
        "Q_DECLARE_OPERATORS_FOR_FLAGS", "Q_PRIVATE_SLOT", "Q_FLAGS", \
        "Q_DECLARE_INTERFACE", "Q_DECLARE_METATYPE","KDE_DUMMY_COMPARISON_OPERATOR",\
        "Q_GADGET", "K_DECLARE_PRIVATE", "PHONON_ABSTRACTBASE", "PHONON_HEIR",\
        "PHONON_OBJECT", "Q_DECLARE_PRIVATE", "QT_BEGIN_HEADER", "QT_END_HEADER",\
        "Q_DECLARE_BUILTIN_METATYPE", "Q_OBJECT_CHECK", "Q_DECLARE_PRIVATE_MI",\
        "KDEUI_DECLARE_PRIVATE", "KPARTS_DECLARE_PRIVATE", "Q_INTERFACES",\
        '__attribute__', 'Q_DISABLE_COPY', 'K_SYCOCATYPE', 'Q_DECLARE_TR_FUNCTIONS',\
        'Q_DECLARE_TYPEINFO']


def QtMacros(extraMacros=[]):
    macros = __QtMacros[:]
    macros.extend(extraMacros)
    return macros

__QtPreprocessSubstitutionMacros = [
        ('Q_SLOTS','slots'),
        ('Q_SIGNALS','signals'),
        (re.compile(r'Q_DECLARE_FLAGS\((.*?),(.*?)\)',re.DOTALL),r'typedef QFlags<\2> \1;'),
        ("KDE_CONSTRUCTOR_DEPRECATED",""),
        ("KDE_DEPRECATED",""),
        ("QT_MOC_COMPAT",""),
        ("Q_SCRIPTABLE","")
        ]
def QtPreprocessSubstitutionMacros(extraMacros=[]):
    macros = __QtPreprocessSubstitutionMacros[:]
    macros.extend(extraMacros)
    return macros

def copyrightNotice():
    return """// Copyright 2011 Simon Edwards <simon@simonzone.com>

//                 Generated by twine2

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU Library General Public License as
// published by the Free Software Foundation; either version 2, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details

// You should have received a copy of the GNU Library General Public
// License along with this program; if not, write to the
// Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""
