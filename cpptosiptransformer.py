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

from sealed import sealed
import sipsymboldata
import cppsymboldata

class CppToSipTransformer(object):
    @sealed
    def __init__(self):
        self._sipsym = None
        self._exportMacros = None
        
    def setExportMacros(self, macroList):
        self._exportMacros = set(macroList) if macroList is not None else None
        
    def convert(self, cpptree):
        self._sipsym = sipsymboldata.SymbolData()
        self._convertScope(cpptree.topScope(),self._sipsym.topScope())
        return self._sipsym
        
    def _convertScope(self,cppScope,destScope):
        for item in cppScope:
            #print("==================================")
            #print(item.format())
            if isinstance(item,cppsymboldata.SymbolData.CppClass):
                self._convertClass(item,destScope)
                
            elif isinstance(item,cppsymboldata.SymbolData.Function):
                self._convertFunction(item,destScope)
                
            elif isinstance(item,cppsymboldata.SymbolData.Variable):
                self._convertVariable(item,destScope)

            elif isinstance(item,cppsymboldata.SymbolData.Namespace):
                self._convertNamespace(item,destScope)

            elif isinstance(item,cppsymboldata.SymbolData.Enum):
                self._convertEnum(item,destScope)

    def _convertFunction(self,cppFunction,destScope):
        isCtor = isinstance(cppFunction,cppsymboldata.SymbolData.Constructor)
        isDtor = isinstance(cppFunction,cppsymboldata.SymbolData.Destructor)
        
        # Private funcions/methods are not copied.
        if cppFunction.access()==cppsymboldata.SymbolData.ACCESS_PRIVATE and not isCtor and not isDtor:
            return
            
        # Ignore these operators.
        if cppFunction.name() in ['operator =', 'operator ++', 'operator --']:
            return
            
        if isCtor:
            sipFunction = self._sipsym.Constructor(destScope,cppFunction.name())
        elif isDtor:
            sipFunction = self._sipsym.Destructor(destScope,cppFunction.name())
        else:
            sipFunction = self._sipsym.Function(destScope,cppFunction.name())
            sipFunction.setReturn(cppFunction.return_())
        sipFunction.setAccess(cppFunction.access())
        sipFunction.setArguments( [self._convertArgument(x) for x in cppFunction.arguments()] )
        if cppFunction.storage()=='static':
            sipFunction.setStorage('static')
                   
    def _convertClass(self,cppClass,parentScope):
        if not self._isClassExported(cppClass):
            return None
    
        sipClass = self._sipsym.SipClass(parentScope, cppClass.name())
        sipClass.setBases(cppClass.bases())
        self._convertScope(cppClass,sipClass)
    
    def _isClassExported(self,cppClass):
        if self._exportMacros is not None:
            if self._exportMacros.isdisjoint( set( (x.name() for x in cppClass.macros()))):
                return False
        return True

    def _convertArgument(self,cppArgument):
        return self._sipsym.Argument(cppArgument.argumentType(), cppArgument.name(), cppArgument.defaultValue())

    def _convertVariable(self,cppVariable,parentScope):
        sipVariable = self._sipsym.Variable(parentScope, cppVariable.name())
        sipVariable.setArgument(self._convertArgument(cppVariable.argument()))
        if cppVariable.storage()=='static':
            sipVariable.setStorage('static')
        return sipVariable
    
    def _convertNamespace(self,cppNamespace,parentScope):
        sipNamespace = self._sipsym.Namespace(parentScope, cppNamespace.name())
        self._convertScope(cppNamespace,sipNamespace)
    
    def _convertEnum(self,cppEnum,parentScope):
        sipEnum = self._sipsym.Enum(parentScope, cppEnum.name())
        for item in cppEnum:
            sipEnum.append(item)
