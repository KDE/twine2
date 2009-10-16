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

import os.path
from sealed import sealed
import sipsymboldata
import cppsymboldata

class CppToSipTransformer(object):
    @sealed
    def __init__(self):
        self._sipsym = None
        self._exportMacros = None
        self._ignoredBaseClasses = []
        self._copyrightNotice = None
        self._cppScope = None
        
    def setExportMacros(self, macroList):
        self._exportMacros = set(macroList) if macroList is not None else None
        
    def setIgnoreBaseClasses(self, baseClassList):
        self._ignoredBaseClasses = baseClassList if baseClassList is not None else []
        
    def setCopyrightNotice(self,noticeText):
        self._copyrightNotice = noticeText
        
    def convert(self, cppScope, sipsymboldata):
        self._cppScope = cppScope
        self._sipsym = sipsymboldata
        sipScope = self._sipsym.newScope()
        sipScope.setHeaderFilename(cppScope.headerFilename())
        
        if self._copyrightNotice is not None:
            for line in self._copyrightNotice.split('\n'):
                comment = self._sipsym.Comment(sipScope)
                comment.setValue(line+'\n')
        
        self._convertScope(cppScope,sipScope)
        return sipScope
        
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

            elif isinstance(item,cppsymboldata.SymbolData.EnumTypedef):
                self._convertEnumTypedef(item,destScope)
                
            elif isinstance(item,cppsymboldata.SymbolData.Typedef):
                self._convertTypedef(item,destScope)
                
    def _convertFunction(self,cppFunction,destScope):
        isCtor = isinstance(cppFunction,cppsymboldata.SymbolData.Constructor)
        isDtor = isinstance(cppFunction,cppsymboldata.SymbolData.Destructor)

        if len(cppFunction.template())!=0:
            # Ignore templated functions.
            return
        
        # Private funcions/methods are not copied.
        if cppFunction.access()==cppsymboldata.SymbolData.ACCESS_PRIVATE and not isCtor and not isDtor:
            return
            
        # Ignore these operators.
        if cppFunction.name() in ['operator =', 'operator ++', 'operator --']:
            return
            
        if isCtor:
            sipFunction = self._sipsym.Constructor(destScope,cppFunction.name(),filename=cppFunction._filename,lineno=cppFunction._lineno)
        elif isDtor:
            sipFunction = self._sipsym.Destructor(destScope,cppFunction.name(),filename=cppFunction._filename,lineno=cppFunction._lineno)
        else:
            sipFunction = self._sipsym.Function(destScope,cppFunction.name(),filename=cppFunction._filename,lineno=cppFunction._lineno)
            sipFunction.setReturn(self._convertArgument(cppFunction.return_()))
        sipFunction.setAccess(cppFunction.access())
        sipFunction.setArguments( [self._convertArgument(x) for x in cppFunction.arguments()] )
        if cppFunction.storage()=='static':
            sipFunction.setStorage('static')
                   
    def _convertClass(self,cppClass,parentScope):
        if not self._isClassExported(cppClass) or cppClass.opaque():
            return None
    
        sipClass = self._sipsym.SipClass(parentScope, cppClass.name(),filename=cppClass._filename,lineno=cppClass._lineno)
        sipClass.setBases( [base for base in cppClass.bases() if base not in self._ignoredBaseClasses] )

        if self._cppScope.headerFilename() is not None:
            includeDirective = self._sipsym.SipDirective(sipClass,"%TypeHeaderCode")
            includeDirective.setBody(
"""%%TypeHeaderCode
#include <%s>
%%End
""" % (self._cppScope.headerFilename(),))
        
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
        if cppVariable.access()!=cppsymboldata.SymbolData.ACCESS_PUBLIC:
            return
            
        sipVariable = self._sipsym.Variable(parentScope, cppVariable.name())
        sipVariable.setArgument(self._convertArgument(cppVariable.argument()))
        if cppVariable.storage()=='static':
            sipVariable.setStorage('static')
        sipVariable.setAccess(cppVariable.access())
        return sipVariable
    
    def _convertNamespace(self,cppNamespace,parentScope):
        sipNamespace = self._sipsym.Namespace(parentScope, cppNamespace.name())
        self._convertScope(cppNamespace,sipNamespace)
        if len(sipNamespace)==0:
            del parentScope[parentScope.index(sipNamespace)]
    
    def _convertEnum(self,cppEnum,parentScope):
        sipEnum = self._sipsym.Enum(parentScope, cppEnum.name())
        sipEnum.setAccess(cppEnum.access())
        for item in cppEnum:
            sipEnum.append(item)

    def _convertTypedef(self,cppTypedef,parentScope):
        sipTypedef = self._sipsym.Typedef(parentScope, cppTypedef.name(),
            filename=cppTypedef._filename,lineno=cppTypedef._lineno)
        sipTypedef.setAccess(cppTypedef.access())
        sipTypedef.setArgumentType(cppTypedef.argumentType())
        return sipTypedef
        
    def _convertEnumTypedef(self,cppEnumTypedef,parentScope):
        sipEnum = self._sipsym.Enum(parentScope, cppEnumTypedef.name())
        sipEnum.setAccess(cppEnumTypedef.enum().access())
        for item in cppEnumTypedef.enum():
            sipEnum.append(item)
        return sipEnum

###########################################################################
def ExpandClassNames(sipsym,scope):
    for item in scope:
        if isinstance(item,sipsym.SipClass):
            _ExpandClassNamesForClass(sipsym,item)
            
        elif isinstance(item,sipsym.Namespace):
            ExpandClassNames(sipsym,item)
            
        elif isinstance(item,sipsym.Constructor):
            _ExpandClassNamesForArguments(sipsym,scope,item)
            
        elif isinstance(item,sipsym.Function):
            _ExpandClassNamesForFunction(sipsym,scope,item)

def _ExpandClassNamesForClass(sipsym,sipClass):
    # Use FQNs when talking about base classes, otherwise SIP fails.
    fqnBaseList = []
    for base in sipClass.bases():
        try:
            baseObject = sipsym.lookupType(base,sipClass.parentScope())
            fqnBaseList.append(baseObject.fqName())
        except KeyError:
            fqnBaseList.append(base)
    sipClass.setBases(fqnBaseList)
    
    ExpandClassNames(sipsym,sipClass)

def _ExpandClassNamesForFunction(sipsym,context,sipFunction):
    sipFunction.setReturn(_ExpandArgument(sipsym,context,sipFunction.return_()))
    
    _ExpandClassNamesForArguments(sipsym,context,sipFunction)
    
def _ExpandClassNamesForArguments(sipsym,context,sipFunction):
    sipFunction.setArguments( [_ExpandArgument(sipsym,context,argument) for argument in sipFunction.arguments()] )

_PrimitiveTypes = ["char","signed char","unsigned char","wchar_t","int","unsigned",
    "unsigned int","short","unsigned short","long","unsigned long","long long",
    "unsigned long long","float","double","bool","void"]

def _ExpandArgument(sipsym,context,argument):
    className = argument.argumentType()
    
    suffix = ""
    if className.endswith('*'):
        className = className[:-1]
        suffix = '*'
    if className.endswith('&'):
        className = className[:-1]
        suffix = '&'
        
    prefix = ""
    if className.startswith("const "):
        className = className[6:]
        prefix = "const "
    
    #if '<' in className:
    #    return argument
    if className not in _PrimitiveTypes:
        #    return argument
        try:
            classObject = sipsym.lookupType(className,context)
            if classObject.fqName()==className:
                return argument # Nothing to do.
            className = classObject.fqName()
        except KeyError:
            print("Warning: %s Unrecognized type '%s' was found when expanding argument type names." % (context.sourceLocation(),className))
            return argument

    defaultValue = argument.defaultValue()
    if defaultValue is not None:
        if defaultValue.endswith("()"):
            try:
                valueObject = sipsym.lookupType(defaultValue[:-2],context)
                defaultValue = valueObject.fqName() + "()"
            except KeyError:
                pass
        else:
            enum = sipsym.lookupEnum(defaultValue,context)
            if enum is not None:
                defaultValue =  enum.fqName() + "::" + defaultValue
            else:
                try:
                    valueObject = sipsym.lookupType(defaultValue,context)
                    defaultValue = valueObject.fqName()
                except KeyError:
                    pass
                
            
    newArgument = sipsym.Argument(prefix + className + suffix, argument.name(), defaultValue,
                    argument.template(), argument.defaultTypes())
    newArgument.setAnnotations(argument.annotations())
    return newArgument
    
###########################################################################
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

###########################################################################

def UpdateConvertToSubClassCodeDirectives(symbolData,scopeList,ignoreClassList=[]):
    """Insert of update CTSCC directives
    
    Insert or update the Sip ConvertToSubClassCode directives in the given list of scopes.
    
    Keyword arguments:
    symbolData -- 
    scopeList -- List of scopes containing the classes which need to be updated.
    ignoreClassList -- List of class names which should be ignored.
    """
    _UpdateConvertToSubClassCodeDirectives(symbolData,scopeList,ignoreClassList).run()

class _UpdateConvertToSubClassCodeDirectives(object):
    def __init__(self,symbolData,scopeList,ignoreClassList):
        self._symbolData = symbolData
        self._scopeList = scopeList
        self._ignoreClassList = ignoreClassList
        self._subclassList = None
        self.INDENT = "    "
        
    def run(self):
        if len(self._scopeList)==0:
            return
        
        # Collect all of the classes that we need to consider.
        self._classList = self._findClasses(self._scopeList)
        
        # Filter out uninteresting classes from the _classList.
        self._subclassList = [class_ for class_ in self._classList
            if len(class_.bases())!=0 and class_.name() not in self._ignoreClassList]
        
        # Build a mapping from class objects to their subclasses.
        classToSubclassMapping = {}
        topSuperClasses = set()
        for class_ in self._subclassList:
            topSuperClass = self._updateSubclassBaseMapping(classToSubclassMapping,class_)
            if topSuperClass is None:
                topSuperClass = class_
            topSuperClasses.add(topSuperClass)
        
        for class_ in topSuperClasses:
            self._insertCTSCC(classToSubclassMapping,class_)
            
    def _updateSubclassBaseMapping(self,mapping,class_):
        lastBase = None
        for baseName in class_.bases():
            try:
                base = self._symbolData.lookupType(baseName,class_.parentScope())
                if lastBase is None:
                    lastBase = base
                subClassList = mapping.setdefault(base,set())
                subClassList.add(class_)
                top = self._updateSubclassBaseMapping(mapping,base)
                if top is not None:
                    lastBase = top
            except KeyError:
                print("Warning: %s Unrecognized type '%s' was found when updating CTSCC." % (class_.sourceLocation(),baseName))
        return lastBase

    def _generateCTSCC(self,classToSubclassMapping,class_):
        return "%%ConvertToSubClassCode\n    // CTSCC for subclasses of '%s'\n    sipClass = NULL;\n\n%s%%End\n" % (class_.name(),self._generateCTSCCPart(classToSubclassMapping,class_,self.INDENT))
            
    def _generateCTSCCPart(self,classToSubclassMapping,class_,indent="",joiner=""):
        accu = []
        
        subclasses = list(classToSubclassMapping.get(class_,set()))
        def namekey(class_): return class_.fqName()
        subclasses.sort(key=namekey)
        
        if class_ in self._subclassList:
            accu.append(indent)
            accu.append(joiner)
            joiner = ""
            accu.append("if (dynamic_cast<")
            accu.append(class_.fqName())
            accu.append("*>(sipCpp))\n")
            if len(subclasses)!=0:
                accu.append(indent);
                accu.append(self.INDENT)
                accu.append("{\n")
                
            if class_ in self._subclassList:
                accu.append(indent)
                accu.append(self.INDENT)
                accu.append("sipClass = sipClass_")
                accu.append(class_.fqName().replace("::","_"))
                accu.append(";\n")
            extraIndent = self.INDENT                
        else:
            extraIndent = ""
        
        for subclass in subclasses:
            accu.append(self._generateCTSCCPart(classToSubclassMapping,subclass,indent+extraIndent,joiner))
            joiner = "else "
        
        if class_ in self._subclassList and len(subclasses)!=0:
            accu.append(indent)
            accu.append(self.INDENT)
            accu.append("}\n")

        return "".join(accu)
        
    def _insertCTSCC(self,classToSubclassMapping,class_):
        subclasses = self._findAllSubclasses(classToSubclassMapping,class_)
        
        # Find an existing %ConvertToSubClassCode block.
        directiveClass = None
        for subclass in subclasses:
            directive = self._findDirective(subclass,"%ConvertToSubClassCode")
            if directive is not None:
                directiveClass = subclass
                break
        else:
            # Create a new %ConvertToSubClassCode block.
            # Try the root first.
            if class_ in self._classList:
                directiveClass = class_
            else:
                # Choose a subclass, use the first one by name.
                def namekey(class_): return class_.name()
                subclasses.sort(key=namekey)
                directiveClass = subclasses[0]
            directive = self._symbolData.SipDirective(directiveClass,"%ConvertToSubClassCode")
        directive.setBody(self._generateCTSCC(classToSubclassMapping,class_))
        
        # Update the %TypeHeaderCode #include list.
        headerCode = self._findDirective(directiveClass.topScope(),"%ModuleHeaderCode")
        if headerCode is None:
            headerCode = self._symbolData.SipDirective(directiveClass.topScope(),"%ModuleHeaderCode")
        
        fileScopes = list(set( (subclass.topScope().headerFilename() for subclass in subclasses) ))
        def key(x): return os.path.basename(x)
        fileScopes.sort(key=key)
        
        headerCode.setBody("%ModuleHeaderCode\n//ctscc\n" +
            "".join(["#include <"+str(x)+">\n" for x in fileScopes]) +
            "%End\n")
        
    def _findDirective(self,class_,directiveName):
        for item in class_:
            if isinstance(item,self._symbolData.SipDirective):
                if item.name()==directiveName:
                    return item
        return None

    def _findAllSubclasses(self,classToSubclassMapping,class_):
        result = []
        if class_ in self._subclassList:
            result.append(class_)
        for subclass in classToSubclassMapping.get(class_,[]):
            result.extend(self._findAllSubclasses(classToSubclassMapping,subclass))
        return result
        
    def _findClasses(self,scope):
        classList = []
        for item in scope:
            if isinstance(item,self._symbolData.SipClass):
                classList.append(item)
            if isinstance(item,self._symbolData.Entity):
                classList.extend(self._findClasses(item))
        return classList
    
###########################################################################
def SanityCheckSip(symbolData,scopeList):
    _SanityCheckSip(symbolData,scopeList).run()
    
class _SanityCheckSip(object):
    def __init__(self,symbolData,scopeList):
        self._symbolData = symbolData
        self._scopeList = scopeList
        
    def run(self):
        for scope in self._scopeList:
            self._checkScope(scope)
            
    def _checkScope(self,scope):
        for item in scope:
            if isinstance(item,self._symbolData.SipClass):
                self._checkClass(item)
            elif isinstance(item,self._symbolData.Function):
                self._checkFunction(item)
                
    def _checkClass(self,sipClass):
        # Check the base classes.
        for baseName in sipClass.bases():
            try:
                self._symbolData.lookupType(baseName,sipClass.parentScope())
            except KeyError:
                print("Error: %s Unknown base class '%s'" % (sipClass.sourceLocation(),baseName))
    
        for item in sipClass:
            if isinstance(item,self._symbolData.Constructor) or isinstance(item,self._symbolData.Destructor) or \
            isinstance(item,self._symbolData.Function):
                self._checkFunction(item)

    def _checkFunction(self,function):
        if function.ignore():
            return

        for arg in function.arguments():
            if arg.argumentType().endswith('&') and 'In' not in arg.annotations() and 'Out' not in arg.annotations():
                print("Error: %s Parameter '%s' requires a /In/ or /Out/ annotation." % (function.sourceLocation(),arg.name()))
