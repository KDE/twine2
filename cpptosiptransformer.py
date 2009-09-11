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
        self._ignoredBaseClasses = []
        
    def setExportMacros(self, macroList):
        self._exportMacros = set(macroList) if macroList is not None else None
        
    def setIgnoreBaseClasses(self, baseClassList):
        self._ignoredBaseClasses = baseClassList if baseClassList is not None else []
        
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
            sipFunction.setReturn(self._convertArgument(cppFunction.return_()))
        sipFunction.setAccess(cppFunction.access())
        sipFunction.setArguments( [self._convertArgument(x) for x in cppFunction.arguments()] )
        if cppFunction.storage()=='static':
            sipFunction.setStorage('static')
                   
    def _convertClass(self,cppClass,parentScope):
        if not self._isClassExported(cppClass):
            return None
    
        sipClass = self._sipsym.SipClass(parentScope, cppClass.name())
        sipClass.setBases( [base for base in cppClass.bases() if base not in self._ignoredBaseClasses] )
        self._convertScope(cppClass,sipClass)
    
    def _isClassExported(self,cppClass):
        if self._exportMacros is not None:
            if self._exportMacros.isdisjoint( set( (x.name() for x in cppClass.macros()))):
                return False
        return True

    def _convertArgument(self,cppArgument):
        argumentType = cppArgument.argumentType()
        argumentType = {
            'short int': 'short',
            'unsigned short int': 'unsigned short',
            'long unsigned int': 'unsigned long'
            }.get(argumentType,argumentType)
        
        defaultValue = cppArgument.defaultValue()
        if defaultValue=='true':
            defaultValue = '1'
        if defaultValue=='false':
            defaultValue = '0'
            
        return self._sipsym.Argument(argumentType, cppArgument.name(), defaultValue)

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

class MethodAnnotationRule(object):
    @sealed
    def __init__(self,methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations):
        self._methodTypeMatch = methodTypeMatch
        
        if parameterTypeMatch=='*':
            self._parameterTypeMatch = None
        else:
            self._parameterTypeMatch = set([parameterTypeMatch]) if isinstance(parameterTypeMatch,str) else set(parameterTypeMatch)
        
        self._parameterNameMatch = set([parameterNameMatch]) if isinstance(parameterNameMatch,str) else set(parameterNameMatch)
        self._annotations = [annotations] if isinstance(annotations,str) else annotations
       
    def apply(self,symbolData,sipFunction):
        matchCtor = self._methodTypeMatch in ('ctor','all')
        matchDtor = self._methodTypeMatch in ('dtor','all')
        matchAny = self._methodTypeMatch=='all'

        if (matchCtor and isinstance(sipFunction,symbolData.Constructor)) or \
                (matchDtor and isinstance(sipFunction,symbolData.Destructor)) or \
                matchAny:
            for argument in sipFunction.arguments():
                if self._parameterTypeMatch is None or argument.argumentType() in self._parameterTypeMatch:
                    if argument.name() in self._parameterNameMatch:
                        newAnnotations = list(argument.annotations())
                        for anno in self._annotations:
                            if anno not in newAnnotations:
                                newAnnotations.append(anno)
                                argument.setAnnotations(newAnnotations)
            
    def __str__(self):
        return "ClassMatch: " + repr(self._classMatch) + " MethodTypeMatch: " + methodTypeMatch + \
            " MethodNameMatch: " + repr(methodNameMatch) + " Annotations: " + repr(self._annotations)

class SipAnnotator(object):
    @sealed
    def __init__(self):
        self._methodAnnotationRules = None
        self._sipsym = sipsymboldata.SymbolData()

    def setMethodAnnotationRules(self,rules):
        self._methodAnnotationRules = rules
        
    def applyRules(self,sipTree):
        for item in sipTree:
            if isinstance(item,self._sipsym.SipClass):
                self._applyRulesToClass(item)
                
    def _applyRulesToClass(self,sipClass):
        for item in sipClass:
            if isinstance(item,self._sipsym.Function):
                self._applyRulesToFunction(self._methodAnnotationRules,item)
            elif isinstance(item,self._sipsym.Constructor):
                self._applyRulesToFunction(self._methodAnnotationRules,item)
            elif isinstance(item,self._sipsym.Destructor):
                self._applyRulesToFunction(self._methodAnnotationRules,item)
                
        self.applyRules(sipClass)
        
    def _applyRulesToFunction(self,rules,sipFunction):
        for rule in rules:
            rule.apply(self._sipsym, sipFunction)
