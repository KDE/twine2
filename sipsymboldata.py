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
import cppsymboldata

class SymbolData(cppsymboldata.SymbolData):
    @sealed
    def __init__(self):
        cppsymboldata.SymbolData.__init__(self)
        self._classIndex = None
        
    def lookupClass(self,name):
        if self._classIndex is None:
            self._buildClassIndex()

        return self._classIndex[name]

    def _buildClassIndex(self):
        self._classIndex = {}
        self._indexScope(self.topScope())
        for scope in self._scopes:
            self._indexScope(scope)

    def _indexScope(self,scope):
        for item in scope:
            if isinstance(item,SymbolData.SipClass):
                self._classIndex[item.name()] = item
            elif isinstance(item,SymbolData.Namespace):
                self._indexScope(self,item)

    class _SipEntityExtra(object):
        @sealed
        def __init__(self):
            self._annotations = None
            self._blocks = []
            self._ignore = False
            self._cppargs = None
            self._cppreturn = None
            self._force = False
            
        def isIgnore(self):
            return self._ignore
            
        def setIgnore(self,ignore):
            self._ignore = ignore
            
        def setForce(self,force):
            self._force = force
            
        def force(self):
            return self._force
            
        def setAnnotations(self,annotations):
            self._annotations = annotations
            
        def setCppArgs(self,cppArgs):
            self._cppargs = cppArgs
            
        def setCppReturn(self,cppreturn):
            self._cppreturn = cppreturn
            
        def addBlock(self, block):
            self._blocks.append(block)
            
        def _formatIgnore(self,indent):
            if self._ignore:
                return "//ig" + (" " if indent==0 else "")
            else:
                return ""
                
        def _formatCppArgs(self):
            if self._cppargs is not None:
                return (" [(" if self._cppreturn is None else "  [" + self._cppreturn + " (") + \
                    ", ".join(item.format() for item in self._cppargs) + ")]"
            else:
                return ""

    class SipClass(cppsymboldata.SymbolData.CppClass, _SipEntityExtra):
        @sealed
        def __init__(self,parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.CppClass.__init__(self, parentScope, name, filename, lineno)
            SymbolData._SipEntityExtra.__init__(self)

        def allSuperClassNames(self):
            """Get all super class names
            
            A set of super class names."""
            symbolData = self._symbolData()
            allBases = set()
            for name in self._bases:
                allBases.add(name)
                
                class_ = symbolData.lookupClass(name)
                if class_ is not None:
                    allBases.update(class_.allSuperClassNames())
                    
            return allBases

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            
            if self._ignore:
                accu.append(self._formatIgnore(indent))
            else:
                accu.append(pre)
            accu.append("class ")
            
            accu.append(self._name)
            if not self._opaque:
                if len(self._bases):
                    accu.append(" : ")
                    accu.append(', '.join(self._bases))
                    
                if self._annotations is not None and len(self._annotations)!=0:
                    accu.append(' /')
                    accu.append(','.join(self._annotations))
                    accu.append('/')
                accu.append("\n")
                accu.append(pre)
                accu.append("{\n")

                access = SymbolData.ACCESS_PRIVATE
                force = False
                for item in self._items:
                    if isinstance(item,cppsymboldata.SymbolData._CppEntity):
                        if item.access() is not access:
                            accu.append(pre)
                            accu.append(item.formatAccess())
                            accu.append(":\n")
                            access = item.access()
                        if item.force()!=force:
                            if not force:
                                accu.append("//force\n")
                            else:
                                accu.append("//end\n")
                            force = not force
                    accu.append(item.format(indent+1))
                if force:
                    accu.append("//end\n")
                
                accu.append(pre)
                accu.append("};\n")
            else:
                accu.append(";\n")
            return ''.join(accu)

    class Argument(cppsymboldata.SymbolData.Argument):
        @sealed
        def __init__(self, argumentType, argumentName = None, argumentValue = None, template = None, defaultTypes = None):
            cppsymboldata.SymbolData.Argument.__init__(self, argumentType, argumentName, argumentValue, template, defaultTypes)
            self._annotations = None

        def setAnnotations(self,annotations):
            self._annotations = annotations
            
        def annotations(self):
            return self._annotations
        
        def format(self):
            annos = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annos = " /" + ",".join(self._annotations) + "/"
            return self._argumentType + (" " + self._argumentName if self._argumentName is not None else "") + \
                annos + \
                ("" if self._defaultValue is None else " = "+self._defaultValue)

    class FunctionArgument(Argument):
        @sealed
        def __init__(self, argumentName, returnType, functionArguments):
            SymbolData.Argument.__init__(self,None, argumentName)
            self._returnType = returnType
            self._functionArguments = functionArguments
            
        def format(self):
            return self._returnType + " (*" + self._argumentName + ")("+self._functionArguments+")"

    class Function(cppsymboldata.SymbolData.Function, _SipEntityExtra):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Function.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)

        def format(self,indent=0):
            annotations = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annotations = ' /' + ', '.join(self._annotations) + '/'
            
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Function.format(self,indent)[:-2] + \
                annotations + self._formatCppArgs() + ";\n" + \
                ''.join( (block.format(indent) for block in self._blocks))

    class Constructor(cppsymboldata.SymbolData.Constructor, _SipEntityExtra):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Constructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            annotations = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annotations = ' /' + ', '.join(self._annotations) + '/'
            
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Constructor.format(self,indent)[:-2] + \
                annotations + self._formatCppArgs() + ";\n" + \
                ''.join( (block.format(indent) for block in self._blocks))

    class Destructor(cppsymboldata.SymbolData.Destructor, _SipEntityExtra):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Destructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            annotations = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annotations = ' /' + ', '.join(self._annotations) + '/'
            
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Destructor.format(self,indent)[:-2] + \
                annotations + self._formatCppArgs() + ";\n" + \
                ''.join( (block.format(indent) for block in self._blocks))
            
    class Variable(cppsymboldata.SymbolData.Variable, _SipEntityExtra):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Variable.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Variable.format(self,indent)

    class SipBlock(object):
        @sealed
        def __init__(self, name):
            self._name = name
            self._body = None

        def setBody(self, body):
            self._body = body

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return self._body + '\n'

    class SipDirective(cppsymboldata.SymbolData.ScopedEntity, SipBlock):
        @sealed
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.ScopedEntity.__init__(self, parentScope, filename, lineno)
            SymbolData.SipBlock.__init__(self, name)
            
    class Comment(cppsymboldata.SymbolData.ScopedEntity):
        @sealed
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData.ScopedEntity.__init__(self, parentScope, filename, lineno)
            self._comment = None
            
        def setValue(self,comment):
            self._comment = comment
            
        def format(self,indent=0):
            return self._comment

    class Template(cppsymboldata.SymbolData._CppEntity,cppsymboldata.SymbolData.Scope,_SipEntityExtra):
        @sealed
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData._CppEntity.__init__(self, parentScope, None, filename, lineno)
            cppsymboldata.SymbolData.Scope.__init__(self)
            SymbolData._SipEntityExtra.__init__(self)
            self._parameters = None
            
        def setParameters(self,parameters):
            self._parameters = parameters
            
        def insertIntoScope(self, name, cppMember):
            cppsymboldata.SymbolData.Scope.insertIntoScope(self,name,cppMember)
            self._scope.insertIntoScope(name, self)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return pre + 'template <' + self._parameters + '>\n' + cppsymboldata.SymbolData.Scope.format(self,indent)
            
    class SipType(cppsymboldata.SymbolData.ScopedEntity, SipBlock):
        @sealed
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData.ScopedEntity.__init__(self, parentScope, filename, lineno)
            SymbolData.SipBlock.__init__(self, None)

    class Enum(cppsymboldata.SymbolData.Enum, _SipEntityExtra):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Enum.__init__(self, parentScope, name, filename, lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            accu.append(pre)
            accu.append("enum")
            if self._name is not None:
                    accu.append(" ")
                    accu.append(self._name)
            accu.append("\n")
            accu.append(pre)
            accu.append("{\n")
            
            pre2 = SymbolData._indentString(indent+1)
            num_enums = sum( (1 for e in self._enumerators if isinstance(e,cppsymboldata.SymbolData.Enumerator)) )
            enum_count = 0
            for item in self._enumerators:
                accu.append(pre2)
                if isinstance(item,cppsymboldata.SymbolData.Enumerator):
                    accu.append(item.format())
                    enum_count += 1
                    if enum_count!=num_enums:
                        accu.append(",")
                    accu.append("\n")
                else:
                    accu.append(item.format())
            accu.append(pre)
            accu.append("};\n")
            return ''.join(accu)
        
    class EnumeratorComment(object):
        @sealed
        def __init__(self,body):
            self._body = body
            
        def format(self):
            return self._body

    class Typedef(cppsymboldata.SymbolData.Typedef, _SipEntityExtra):
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Typedef.__init__(self,parentScope, name, filename, lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Typedef.format(self,indent)
            
    class FunctionPointerTypedef(Typedef):
        @sealed
        def __init__(self,parentScope, functionArgument, filename, lineno):
            SymbolData.Typedef.__init__(self,parentScope, functionArgument.name(), filename, lineno)
            self._functionArgument = functionArgument
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return self._formatIgnore(indent) + pre + "typedef "+ self._functionArgument.format() + ";\n"
            
    class Namespace(cppsymboldata.SymbolData.Namespace):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Namespace.__init__(self, parentScope, name, filename, lineno)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            accu.append(pre)
            accu.append("namespace ")
            accu.append(self._name)
            accu.append("\n")
            accu.append(pre)
            accu.append("{\n")
           
            force = False
            for item in self._items:
                if isinstance(item,cppsymboldata.SymbolData._CppEntity):
                    if item.force()!=force:
                        if not force:
                            accu.append("//force\n")
                        else:
                            accu.append("//end\n")
                        force = not force
                accu.append(item.format(indent))
            if force:
                accu.append("//end\n")
            
            accu.append(pre)
            accu.append("};\n")
            return "".join(accu)
