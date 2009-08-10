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

import cppsymboldata

class SymbolData(cppsymboldata.SymbolData):
    def __init__(self):
        cppsymboldata.SymbolData.__init__(self)

    class SipClass(cppsymboldata.SymbolData.CppClass):
        def __init__(self,parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.CppClass.__init__(self, parentScope, name, filename, lineno)
            
    class _SipFunctionExtra(object):
        def __init__(self):
            self._annotation = None
            
        def setAnnotation(self,annotation):
            self._annotation = annotation
            
        def setCppArgs(self,cppArgs):
            pass
            
    class Function(cppsymboldata.SymbolData.Function, _SipFunctionExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Function.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipFunctionExtra.__init__(self)
            
    class Constructor(cppsymboldata.SymbolData.Constructor, _SipFunctionExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Constructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipFunctionExtra.__init__(self)
            
    class Destructor(cppsymboldata.SymbolData.Destructor, _SipFunctionExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Destructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipFunctionExtra.__init__(self)
        