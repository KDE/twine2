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

    class _SipEntityExtra(object):
        def __init__(self):
            self._annotations = None
            self._blocks = []
            self._ignore = False
            
        def isIgnore(self):
            return self._ignore
            
        def setIgnore(self,ignore):
            self._ignore = ignore
            
        def setAnnotations(self,annotations):
            self._annotations = annotations
            
        def setCppArgs(self,cppArgs):
            pass

        def addBlock(self, block):
            self._blocks.append(block)
            
        def _formatIgnore(self,indent):
            if self._ignore:
                return "//ig" + (" " if indent==0 else "")
            else:
                return ""
            
    class SipClass(cppsymboldata.SymbolData.CppClass, _SipEntityExtra):
        def __init__(self,parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.CppClass.__init__(self, parentScope, name, filename, lineno)
            SymbolData._SipEntityExtra.__init__(self)

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
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
                for item in self._items:
                    if isinstance(item,cppsymboldata.SymbolData._CppEntity) and item.access() is not access:
                        accu.append(pre)
                        accu.append(item.formatAccess())
                        accu.append(":\n")
                        access = item.access()
                    accu.append(item.format(indent+1))
                accu.append(pre)
                accu.append("};\n")
            else:
                accu.append(";\n")
            return ''.join(accu)

    class Argument(cppsymboldata.SymbolData.Argument):
        def __init__(self, argumentType, argumentName = None, argumentValue = None, template = None, defaultTypes = None):
            cppsymboldata.SymbolData.Argument.__init__(self, argumentType, argumentName, argumentValue, template, defaultTypes)
            self._annotations = None

        def setAnnotations(self,annotations):
            self._annotations = annotations
            
        def format(self):
            annos = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annos = " /" + ",".join(self._annotations) + "/"
            return self._argumentType + (" " + self._argumentName if self._argumentName is not None else "") + \
                annos + \
                ("" if self._defaultValue is None else " = "+self._defaultValue)

    class Function(cppsymboldata.SymbolData.Function, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Function.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)

        def format(self,indent=0):
            annotations = ""
            if self._annotations is not None and len(self._annotations)!=0:
                annotations = ' /' + ', '.join(self._annotations) + '/'
            
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Function.format(self,indent)[:-2] + \
                annotations + ";\n" + \
                ''.join( (block.format(indent) for block in self._blocks))

    class Constructor(cppsymboldata.SymbolData.Constructor, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Constructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Constructor.format(self,indent)
            
    class Destructor(cppsymboldata.SymbolData.Destructor, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Destructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Destructor.format(self,indent)
            
    class Variable(cppsymboldata.SymbolData.Variable, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Variable.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
        def format(self,indent=0):
            return self._formatIgnore(indent) + cppsymboldata.SymbolData.Variable.format(self,indent)

    class SipBlock(object):
        def __init__(self, name):
            self._name = name
            self._body = None

        def setBody(self, body):
            self._body = body

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return self._body + '\n'

    class SipDirective(cppsymboldata.SymbolData._ScopedEntity, SipBlock):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData._ScopedEntity.__init__(self, parentScope, filename, lineno)
            SymbolData.SipBlock.__init__(self, name)
            
    class Comment(cppsymboldata.SymbolData._ScopedEntity):
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData._ScopedEntity.__init__(self, parentScope, filename, lineno)
            self._comment = None
            
        def setValue(self,comment):
            self._comment = comment
            
        def format(self,indent=0):
            return self._comment

    class Template(cppsymboldata.SymbolData._CppEntity,cppsymboldata.SymbolData._Scope):
        def __init__(self, parentScope, filename, lineno):
            cppsymboldata.SymbolData._CppEntity.__init__(self, parentScope, None, filename, lineno)
            cppsymboldata.SymbolData._Scope.__init__(self)
            self._parameters = None
            
        def setParameters(self,parameters):
            self._parameters = parameters
            
        def insertIntoScope(self, name, cppMember):
            cppsymboldata.SymbolData._Scope.insertIntoScope(self,name,cppMember)
            self._scope.insertIntoScope(name, self)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return pre + 'template <' + self._parameters + '>\n' + cppsymboldata.SymbolData._Scope.format(self,indent)
