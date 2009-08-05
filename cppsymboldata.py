# -*- coding: utf-8 -*-
#     Copyright 2007-8 Jim Bublitz <jbublitz@nwinternet.com>
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

class SymbolData(object):
    ACCESS_PUBLIC = object()
    ACCESS_PRIVATE = object()
    ACCESS_PROTECTED = object()
    ACCESS_TYPE_MAPPING_FROM_NAME = {
        'public': ACCESS_PUBLIC,
        'private': ACCESS_PRIVATE,
        'protected': ACCESS_PROTECTED
    }

    ACCESS_TYPE_MAPPING_TO_NAME = {}
    for (key,value) in ACCESS_TYPE_MAPPING_FROM_NAME.iteritems():
        ACCESS_TYPE_MAPPING_TO_NAME[value] = key

    def __init__(self):
        self._topScope = self._Scope()

    def topScope(self):
        return self._topScope

    @classmethod
    def _indentString(cls, indent):
        return ' ' * (4*indent)

    # Query interface goes here.

    class _Scope(object):
        def __init__(self):
            self._items = []
            self._names = {}

        def insertIntoScope(self, name, cppMember):
            self._items.append(cppMember)
            self._names[name] = cppMember

        def __str__(self):
            return '\n'.join( (str(item) for item in self._items) )

        def format(self,indent=0):
            return ''.join( (item.format(indent) for item in self._items) )
            
    class Namespace(_Scope):
        def __init__(self, parentScope, name, filename, lineno):
            SymbolData._Scope.__init__(self)
            self._scope = parentScope
            self._name = name
            self._filename = filename
            self._lineno = lineno
            self._scope.insertIntoScope(name, self)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return pre + "namespace " + self._name + " {\n" + SymbolData._Scope.format(self,indent+1) + pre + "};\n"
            
    class Enum(object):
        def __init__(self, parentScope, name, filename, lineno):
            self._scope = parentScope
            self._name = name
            self._filename = filename
            self._lineno = lineno
            self._enumerators = []
            self._scope.insertIntoScope(name, self)
            
        def appendEnumerator(self,enumerator):
            self._enumerators.append(enumerator)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            accu.append(pre)
            accu.append("enum ")
            if self._name is not None:
                    accu.append(self._name)
                    accu.append(" ")
            accu.append("{\n")
            
            pre2 = SymbolData._indentString(indent+1)
            accu.append(pre2)
            accu.append((",\n"+pre2).join((item.format() for item in self._enumerators)))
            accu.append("\n")
            accu.append(pre)
            accu.append("};\n")
            return ''.join(accu)
            
    class Enumerator(object):
        def __init__(self,name,value):
            self._name = name
            self._value = value
            
        def format(self):
            if self._value is None:
                return self._name
            else:
                return self._name + "=" + self._value
            
    class _CppEntity(object):
        def __init__(self, parentScope, name, filename, lineno):
            self._access = SymbolData.ACCESS_PUBLIC
            self._scope = parentScope
            self._name = name
            self._filename = filename
            self._lineno = lineno
            self._scope.insertIntoScope(name, self)

        def setAccess(self,typeName):
            self._access = SymbolData.ACCESS_TYPE_MAPPING_FROM_NAME[typeName]

        def access(self):
            return self._access

        def formatAccess(self):
            return SymbolData.ACCESS_TYPE_MAPPING_TO_NAME[self._access]

        def __str__(self):
            return self.format()

    class CppClass(_Scope, _CppEntity):
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._Scope.__init__(self)
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._bases = []
            
        def addBase(self, base):
            self._bases.append(base)
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            accu.append(pre)
            accu.append("class ")
            accu.append(self._name)
            if len(self._bases):
                accu.append(" : ")
                accu.append(', '.join(self._bases))
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
            return ''.join(accu)

    class Argument(object):
        def __init__(self, argumentType, argumentName = None, argumentValue = None, annotation = None, template = None, defaultTypes = None):
            self._argumentType = argumentType
            self._argumentName = argumentName
            self._defaultValue = argumentValue  # string (no leading '=') of default value/expression
            self._defaultTypes = defaultTypes   # any types pulled out of the default value expression
            self._functionPtr = None
            self._annotation = annotation       # a list of annotations
            #self._attributes = Attributes ()
            self._template = template           # the parsed info from any template-type argument

        def format(self):
            return self._argumentType + (" " + self._argumentName if self._argumentName is not None else "")+ ("" if self._defaultValue is None else "="+self._defaultValue)

    class Variable(_CppEntity):
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._storage = None
            self._argument = None

        def setArgument(self, argument):
            self._argument = argument

        def setStorage(self,storage):
            self._storage = storage
            # "auto", "register", "static", "extern", "mutable"
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            storage = self._storage+" " if self._storage is not None else ""
            return pre + storage + self._argument.format() + ";\n"

    class Function(_CppEntity):
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._return = None
            self._storage = None
            self._arguments = None
            self._qualitifier = None

        def setStorage(self,storage):
            self._storage = storage

        def setReturn(self,return_):
            self._return = return_

        def setArguments(self,arguments):
            self._arguments = arguments

        def setQualifier(self,qualifier):
            self._qualitifier = qualifier

        def format(self,indent=0):
            accu = []
            accu.append(SymbolData._indentString(indent))
            if self._storage is not None:
                accu.append(self._storage)
                accu.append(" ")
            if self._qualitifier is not None:
                accu.append(self._qualitifier)
                accu.append(" ")
            accu.append(self._return.format())
            accu.append(" ")
            accu.append(self._name)
            accu.append("(")
            accu.append(', '.join( (arg.format() for arg in self._arguments) ))
            accu.append(");\n")
            return ''.join(accu)

    class Constructor(Function):
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData.Function.__init__(self, parentScope, name, filename, lineno)

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            storage = self._storage+" " if self._storage is not None else ""
            args = ', '.join( (arg.format() for arg in self._arguments) )
            return pre + storage + self._name + "(" + args + ");\n"
