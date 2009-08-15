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
            self._annotation = None
            self._blocks = []
            
        def setAnnotation(self,annotation):
            self._annotation = annotation
            
        def setCppArgs(self,cppArgs):
            pass

        def addBlock(self, block):
            self._blocks.append(block)

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
                    
                if self._annotation is not None and len(self._annotation)!=0:
                    accu.append(' /')
                    accu.append(','.join(self._annotation))
                    accu.append('/')
                accu.append(" {\n")

                access = SymbolData.ACCESS_PRIVATE
                pre2 = SymbolData._indentString(indent+1)
                for item in self._items:
                    if item.access() is not access:
                        accu.append(pre2)
                        accu.append(item.formatAccess())
                        accu.append(":\n")
                        access = item.access()
                    accu.append(item.format(indent+2))
                accu.append(pre)
                accu.append("};\n")
            else:
                accu.append(";\n")
            return ''.join(accu)


    class Function(cppsymboldata.SymbolData.Function, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Function.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)

        def format(self,indent=0):
            return cppsymboldata.SymbolData.Function.format(self,indent) + \
                ''.join( (block.format(indent) for block in self._blocks))

    class Constructor(cppsymboldata.SymbolData.Constructor, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Constructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
    class Destructor(cppsymboldata.SymbolData.Destructor, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Destructor.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)
            
    class Variable(cppsymboldata.SymbolData.Variable, _SipEntityExtra):
        def __init__(self, parentScope, name, filename, lineno):
            cppsymboldata.SymbolData.Variable.__init__(self,parentScope,name,filename,lineno)
            SymbolData._SipEntityExtra.__init__(self)

    class SipBlock(object):
        def __init__(self, name):
            self._name = name
            self._body = None

        def setBody(self, body):
            self._body = body

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return self._body
