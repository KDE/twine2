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
from argvalidate import accepts,returns,one_of
import types
import cppsymboldata

class SymbolData(cppsymboldata.SymbolData):
    @sealed
    def __init__(self):
        cppsymboldata.SymbolData.__init__(self)
        
    class _SipEntityExtra(object):
        @sealed
        def __init__(self):
            self._annotations = []
            self._blocks = []
            self._ignore = False
            self._cppargs = None
            self._cppreturn = None
            self._force = False
            
        @returns(str)
        def fqPythonName(self):
            parentFqn = self.parentScope().fqPythonName()
            
            if self.name() is None:
                return ""
            
            if parentFqn is not None:
                return parentFqn + "." + self.name()
            else:
                return self.name()
                
        def ignore(self):
            return self._ignore
            
        def setIgnore(self,ignore):
            self._ignore = ignore
            
        def setForce(self,force):
            self._force = force
            
        def force(self):
            return self._force
            
        def setAnnotations(self,annotations):
            self._annotations = annotations
            
        def annotations(self):
            return self._annotations
            
        def setCppArgs(self,cppArgs):
            self._cppargs = cppArgs
            
        def setCppReturn(self,cppreturn):
            self._cppreturn = cppreturn
            
        def addBlock(self, block):
            self._blocks.append(block)
            
        def blocks(self):
            return self._blocks
        
        def setBlocks(self,blocks):
            self._blocks = blocks[:]
        
        def _formatIgnore(self,indent):
            if self._ignore:
                return "//ig" + (" " if indent==0 else "")
            else:
                return ""
                
        def _formatCppArgs(self):
            if self._cppargs is not None:
                return (" [(" if self._cppreturn is None else " [" + self._cppreturn + " (") + \
                    ", ".join(item.format() for item in self._cppargs) + ")]"
            else:
                return ""
                
    class TopLevelScope(cppsymboldata.SymbolData.TopLevelScope):
        @sealed
        def __init__(self,symbolData):
            cppsymboldata.SymbolData.TopLevelScope.__init__(self,symbolData)
            self._module = None
            
        def format(self,indent=0):
            accu = []
            force = False
            for item in self:
                if isinstance(item,cppsymboldata.SymbolData._CppEntity) or isinstance(item,SymbolData.SipDirective):
                    if item.force()!=force:
                        if not force:
                            accu.append("//force\n")
                        else:
                            accu.append("//end\n")
                        force = not force
                accu.append(item.format(indent))
            if force:
                accu.append("//end\n")
                
            return ''.join(accu)
            
        def setModule(self,module):
            self._module = module
            
        def module(self):
            return self._module

        def fqPythonName(self):
            return None

    class SipClass(_SipEntityExtra, cppsymboldata.SymbolData.CppClass):
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
                
                class_ = symbolData.lookupType(name,self)
                if class_ is not None:
                    allBases.update(class_.allSuperClassNames())
                    
            return allBases
            
        def classHierarchy(self):
            symbolData = self._symbolData()
            if len(self._bases)==0:
                return [self]
            base = symbolData.lookupType(self._bases[0],self)
            if base is not None:
                return [self] + base.classHierarchy()
            else:
                return [self]
        
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            
            if self._ignore:
                accu.append(self._formatIgnore(indent))
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
                    if isinstance(item,cppsymboldata.SymbolData._CppEntity) or isinstance(item,SymbolData.SipDirective):
                        if item.force()!=force and force:
                            accu.append("//end\n")
                            force = not force
                            
                    if isinstance(item,cppsymboldata.SymbolData._CppEntity):
                        if item.access() is not access:
                            accu.append(pre)
                            accu.append(item.formatAccess())
                            accu.append(":\n")
                            access = item.access()
                            
                    if isinstance(item,cppsymboldata.SymbolData._CppEntity) or isinstance(item,SymbolData.SipDirective):
                        if item.force()!=force and not force:
                            accu.append("//force\n")
                            force = not force
                            
                    accu.append(item.format(indent+1))
                if force:
                    accu.append("//end\n")
                
                accu.append(pre)
                accu.append("};\n")
            else:
                accu.append(";\n")
            return ''.join(accu)

        def __str__(self):
            return "<SipClass '%s'>" % (self.name(),)

    class Argument(cppsymboldata.SymbolData.Argument):
        # FIXME Make this immutable.
    
        @sealed
        def __init__(self, argumentType, argumentName = None, argumentValue = None, template = None, defaultTypes = None):
            cppsymboldata.SymbolData.Argument.__init__(self, argumentType, argumentName, argumentValue, template, defaultTypes)
            self._annotations = []

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

    class Function(_SipEntityExtra, cppsymboldata.SymbolData.Function):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Function.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)

        def format(self,indent=0):
            accu = []
            
            annotations = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annotations = ' /' + ', '.join(self._annotations) + '/'
            
            accu.append(self._formatIgnore(indent))
            accu.append(cppsymboldata.SymbolData.Function.format(self,indent)[:-2])
            accu.append(annotations)
            accu.append(self._formatCppArgs())
            accu.append(";\n")
            for block in self._blocks:
                accu.append(block.format(indent))
            
            return ''.join(accu)


    class Constructor(_SipEntityExtra, cppsymboldata.SymbolData.Constructor):
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

    class Destructor(_SipEntityExtra, cppsymboldata.SymbolData.Destructor):
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
            
    class Variable(_SipEntityExtra, cppsymboldata.SymbolData.Variable):
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
            
        def name(self):
            return self._name
        
        def setBody(self, body):
            self._body = body
            
        def body(self):
            return self._body
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return self._body + '\n'

    class SipDirective(cppsymboldata.SymbolData.Entity, SipBlock):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Entity.__init__(self, parentScope, name, filename, lineno)
            SymbolData.SipBlock.__init__(self, name)
            self._force = False
            self._keypairs = None
            
        def setForce(self,force):
            self._force = force
            
        def force(self):
            return self._force
            
        def setKeypairs(self, pairlist):
            self._keypairs = pairlist   # A list of key-value tuples.
            
        def format(self,indent=0):
            return SymbolData.SipBlock.format(self,indent)
        
    class Comment(cppsymboldata.SymbolData.Comment):
        @sealed
        def __init__(self, parentScope, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Comment.__init__(self, parentScope, filename, lineno)

    class Template(_SipEntityExtra, cppsymboldata.SymbolData._CppEntity):
        @sealed
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData._CppEntity.__init__(self, parentScope, None, filename, lineno)
            SymbolData._SipEntityExtra.__init__(self)
            self._parameters = None
            
        def setParameters(self,parameters):
            self._parameters = parameters
            
        def insertIntoScope(self, name, cppMember):
            cppsymboldata.SymbolData.Entity.insertIntoScope(self,name,cppMember)
            self._scope.insertIntoScope(name, self)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return pre + 'template <' + self._parameters + '>\n' + cppsymboldata.SymbolData.Entity.format(self,indent)
            
    class SipType(cppsymboldata.SymbolData.Entity, SipBlock):
        @sealed
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData.Entity.__init__(self, parentScope, None, filename, lineno)
            SymbolData.SipBlock.__init__(self, None)

        def format(self,indent=0):
            return SymbolData.SipBlock.format(self,indent)

    class Enum(_SipEntityExtra, cppsymboldata.SymbolData.Enum):
        @sealed
        @accepts(cppsymboldata.SymbolData.Entity,one_of(str,types.NoneType),filename=one_of(str,types.NoneType),lineno=int)
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
        
    class Enumerator(cppsymboldata.SymbolData.Enumerator):
        @sealed
        def __init__(self,name,value):
            cppsymboldata.SymbolData.Enumerator.__init__(self,name,value)

        def format(self):
            return self._name
                
    class EnumeratorComment(object):
        @sealed
        def __init__(self,body):
            self._body = body
            
        def format(self):
            return self._body

    class Typedef(_SipEntityExtra, cppsymboldata.SymbolData.Typedef):
        @sealed
        def __init__(self,parentScope, name, filename=None, lineno=-1):
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
            
    class Namespace(_SipEntityExtra, cppsymboldata.SymbolData.Namespace):
        @sealed
        def __init__(self, parentScope, name, filename=None, lineno=-1):
            cppsymboldata.SymbolData.Namespace.__init__(self, parentScope, name, filename, lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            accu.append(self._formatIgnore(indent))
            accu.append(pre)
            accu.append("namespace ")
            accu.append(self._name)
            if self.ignore():
                accu.append(";\n")
            else:
                accu.append("\n")
                accu.append(pre)
                accu.append("{\n")
            
                force = False
                for item in self._items:
                    if isinstance(item,cppsymboldata.SymbolData._CppEntity) or isinstance(item,SymbolData.SipDirective):
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
