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
from sealed import sealed

RETURN_INDENT = 24

class SymbolData(object):
    """Represent the contents of a C++ header file.
     
    This class and its nested classes can represent the contents of a C++
    header file. `topScope()` returns the top level scope. From here you can
    loop over the contents of the file.
    """
    ACCESS_PUBLIC = object()
    ACCESS_PRIVATE = object()
    ACCESS_PROTECTED = object()
    ACCESS_SIGNALS = object()
    ACCESS_TYPE_MAPPING_FROM_NAME = {
        'public': ACCESS_PUBLIC,
        'private': ACCESS_PRIVATE,
        'protected': ACCESS_PROTECTED,
        'signals': ACCESS_SIGNALS
    }

    ACCESS_TYPE_MAPPING_TO_NAME = {}
    for (key,value) in ACCESS_TYPE_MAPPING_FROM_NAME.iteritems():
        ACCESS_TYPE_MAPPING_TO_NAME[value] = key

    @sealed
    def __init__(self):
        """Instantiate a new SymbolData."""
        self._scopes = []

    def newScope(self):
        scope = self.TopLevelScope(self)
        self._scopes.append(scope)
        return scope

    @classmethod
    def _indentString(cls, indent):
        return ' ' * (4*indent)
        
    def _changed(self):
        pass
        
    # Query interface goes here.
    
    class Entity(object):
        """Represents an entity and a scope which can hold other entities.
        
        This class isn't meant to be used directly but is typically subclassed."""
        @sealed
        def __init__(self, parentScope, name, filename, lineno):
            self._scope = parentScope
            self._filename = filename
            self._lineno = lineno
            if self._scope is not None:
                self._scope.insertIntoScope(None, self)
            self._items = []
            self._name = name
            
        def name(self):
            return self._name
            
        def fqName(self):
            parentFqn = self.parentScope().fqName()
            
            # FIXME name() should never be None. This only happens because the typedef parsing is broken with enums.
            if self.name() is None:
                return ""
            
            if parentFqn is not None:
                return parentFqn + "::" + self.name()
            else:
                return self.name()

        def insertIntoScope(self, name, cppMember):
            if cppMember not in self._items:
                self._items.append(cppMember)
            #if name is not None:
            #    self._names[name] = cppMember
            self._killCache(cppMember)

        def __str__(self):
            return '\n'.join( (str(item) for item in self._items) )

        def format(self,indent=0):
            return ''.join( (item.format(indent) for item in self._items) )

        def lastMember(self):
            return self._items[-1] if len(self._items)!=0 else None
            
        def __len__(self):
            return len(self._items)
        
        def __getitem__(self,key):
            return self._items[key]
            
        def __setitem__(self, key, value):
            oldValue = self_items.get(key,None)
            
            self._items[key] = value
            
            self._killCache(oldValue)
            self._killCache(value)
            
        def __iter__(self):
            return self._items.__iter__()
            
        def __delitem__(self,item):
            self._items.__delitem__(item)
            self._killCache(item)
            
        def index(self,item):
            return self._items.index(item)
            
        def append(self,item):
            self._items.append(item)
            self._killCache(item)
        
        def _killCache(self,targetItem):
            syms = self._symbolData()
            syms._changed()
            
        def parentScope(self):
            return self._scope
            
        def topScope(self):
            return self._scope.topScope()
        
        def _symbolData(self):
            return self._scope._symbolData()
        
        def sourceLocation(self):
            if self._filename is not None:
                return "%s:%i" % (self._filename,self._lineno)
            else:
                return "???:%i" % (self._lineno,)
        
    class TopLevelScope(Entity):
        @sealed
        def __init__(self,symbolData):
            SymbolData.Entity.__init__(self, None, None, None, -1)
            self._symbolDataPtr = symbolData
            self._headerFilename = None

        def _symbolData(self):
            return self._symbolDataPtr
            
        def topScope(self):
            return self
            
        def fqName(self):
            return None
            
        def setHeaderFilename(self,filename):
            self._headerFilename = filename
    
        def headerFilename(self):
            return self._headerFilename
    
        def sourceLocation(self):
            if self._headerFilename is not None:
                return "%s:-1" % (self._headerFilename,)
            else:
                return "???:-1" % (self._headerFilename,)
    
        def parentScope(self):
            return None
        
    class Namespace(Entity):
        """Represents a C++ style namespace."""
        @sealed
        def __init__(self, parentScope, name, filename, lineno):
            SymbolData.Entity.__init__(self, parentScope, name, filename, lineno)

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return pre + "namespace " + self._name + "\n"+pre+"{\n" + SymbolData.Entity.format(self,indent) + pre + "};\n"

    class _CppEntity(Entity):
        @sealed
        def __init__(self, parentScope, name, filename, lineno):
            SymbolData.Entity.__init__(self, parentScope, name, filename, lineno)
            self._access = SymbolData.ACCESS_PUBLIC
            if self._scope is not None:
                self._scope.insertIntoScope(name, self)

        def setAccess(self,typeName):
            if typeName in SymbolData.ACCESS_TYPE_MAPPING_TO_NAME.keys():
                self._access = typeName
            else:
                self._access = SymbolData.ACCESS_TYPE_MAPPING_FROM_NAME[typeName]

        def access(self):
            return self._access

        def formatAccess(self):
            return SymbolData.ACCESS_TYPE_MAPPING_TO_NAME[self._access]

        def __str__(self):
            return self.format()
            
    class Enum(_CppEntity):
        @sealed
        def __init__(self, parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._enumerators = []
            
        def fqName(self):
            if self.name() is None:
                return None
                
            parentFqn = self.parentScope().fqName()
            if parentFqn is not None:
                return parentFqn + "::" + self.name()
            else:
                return self.name()
            
        def appendEnumerator(self,enumerator):
            self.append(enumerator)
            
        def append(self,enumerator):
            self._enumerators.append(enumerator)
            
        def __len__(self):
            return len(self._enumerators)
        
        def __getitem__(self,key):
            return self._enumerators[key]
            
        def __setitem__(self, key, value):
            self._enumerators[key] = value
            
        def __iter__(self):
            return self._enumerators.__iter__()
            
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
            accu.append(pre2)
            accu.append((",\n"+pre2).join((item.format() for item in self._enumerators)))
            accu.append("\n")
            accu.append(pre)
            accu.append("};\n")
            return ''.join(accu)
            
    class Enumerator(object):
        @sealed
        def __init__(self,name,value):
            self._name = name
            self._value = value
            
        def name(self):
            return self._name
            
        def value(self):
            return self._value
            
        def format(self):
            if self._value is None:
                return self._name
            else:
                return self._name + "=" + self._value

    class CppClass(_CppEntity):
        @sealed
        def __init__(self,parentScope, name, filename=None, lineno=-1):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._bases = []
            self._opaque = False
            self._macros = []

        def addBase(self, base):
            self._bases.append(base)
            
        def setBases(self,baseList):
            self._bases = baseList
        
        def bases(self):
            """List of base class names
            
            Returns a list of string base class names."""
            return self._bases
        
        def setOpaque(self,opaque):
            self._opaque = opaque
            
        def opaque(self):
            return self._opaque
            
        def addMacro(self,macro):
            self._macros.append(macro)
            
        def macros(self):
            return self._macros
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            accu = []
            accu.append(pre)
            accu.append("class ")
            
            for macro in self._macros:
                accu.append(macro.name())
                accu.append(" ")
            
            accu.append(self._name)
            if not self._opaque:
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
            else:
                accu.append(";\n")
            return ''.join(accu)

    class Argument(object):
        # Immutable.
        
        @sealed
        def __init__(self, argumentType, argumentName = None, argumentValue = None, template = None, defaultTypes = None):
            self._argumentType = argumentType
            self._argumentName = argumentName
            self._defaultValue = argumentValue  # string (no leading '=') of default value/expression
            self._defaultTypes = defaultTypes   # any types pulled out of the default value expression
            self._functionPtr = None
            #self._attributes = Attributes ()
            self._template = template           # the parsed info from any template-type argument

        def argumentType(self):
            return self._argumentType
            
        def name(self):
            return self._argumentName
            
        def defaultValue(self):
            return self._defaultValue
            
        def template(self):
            return self._template
            
        def defaultTypes(self):
            return self._defaultTypes
            
        def format(self):
            return self._argumentType + (" " + self._argumentName if self._argumentName is not None else "") + \
                ("" if self._defaultValue is None else " = "+self._defaultValue)
            
    class FunctionArgument(Argument):
        # Immutable
        @sealed
        def __init__(self, argumentName, returnType, functionArguments):
            SymbolData.Argument.__init__(self,None, argumentName)
            self._returnType = returnType
            self._functionArguments = functionArguments
            
        def format(self):
            return self._returnType + " (*" + self._argumentName + ")("+self._functionArguments+")"
            
    class Variable(_CppEntity):
        """Represents a single variable declaration."""
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._storage = None
            self._argument = None
            self._bitfield = None
            
        def setArgument(self, argument):
            self._argument = argument
            
        def argument(self):
            return self._argument
            
        def setStorage(self,storage):
            self._storage = storage
            # "auto", "register", "static", "extern", "mutable"
            
        def storage(self):
            return self._storage
            
        def setBitfield(self,bitfield):
            self._bitfield = bitfield
            
        def bitfield(self):
            return self._bitfield
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            storage = self._storage+" " if self._storage is not None else ""
            bitfield = " : " + self._bitfield if self._bitfield is not None else ""
            return pre + storage + self._argument.format() + bitfield + ";\n"

    class Function(_CppEntity):
        """Represents a C++ function or method if the parent scope is a class."""
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._return = None
            self._storage = None
            self._arguments = []
            self._qualifier = set()

        def setStorage(self,storage):
            self._storage = storage

        def storage(self):
            return self._storage
            
        def setReturn(self,return_):
            self._return = return_

        def return_(self):
            return self._return

        def setArguments(self,arguments):
            self._arguments = tuple(arguments)

        def arguments(self):
            return self._arguments

        def addQualifier(self,qualifier):
            self._qualifier.add(qualifier)

        def format(self,indent=0):
            accu = []
            accu.append(SymbolData._indentString(indent))
            chars = 0
            if 'virtual' in self._qualifier:
                accu.append("virtual ")
                chars += 8
            if self._storage is not None:
                accu.append(self._storage)
                accu.append(" ")
                chars += len(self._storage) + 1
                
            ret = self._return.format()
            accu.append(ret)
            if (len(ret)+chars) < (RETURN_INDENT-1):
                accu.append(' ' * (RETURN_INDENT-len(ret)-chars))
            else:
                accu.append("  ")
                
            accu.append(self._name)
            accu.append(" (")
            accu.append(', '.join( (arg.format() for arg in self._arguments) ))
            accu.append(")")
            if 'pure' in self._qualifier:
                accu.append("=0")
            if 'const' in self._qualifier:
                accu.append(" const")
            accu.append(";\n")
            return ''.join(accu)

    class Constructor(Function):
        """Represents a constructor."""
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData.Function.__init__(self, parentScope, name, filename, lineno)

        def format(self,indent=0):
            accu = []
            accu.append(SymbolData._indentString(indent))
            ret = (self._storage+" " if self._storage is not None else "") + \
                ("explicit " if 'explicit' in self._qualifier else "")
            accu.append(ret)
            if len(ret) < (RETURN_INDENT-1):
                accu.append(' ' * (RETURN_INDENT-len(ret)))
            else:
                accu.append("  ")
            accu.append(self._name)
            accu.append(" (")
            accu.append(', '.join( (arg.format() for arg in self._arguments) ))
            accu.append(");\n")
            return ''.join(accu)
            
    class Destructor(Function):
        """Represents a destructor."""
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData.Function.__init__(self, parentScope, name, filename, lineno)

        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            storage = self._storage+" " if self._storage is not None else ""
            return pre + storage + "~" + self._name + " ();\n"
            
    class Typedef(_CppEntity):
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._argumentType = None
            
        def setArgumentType(self,argumentType):
            self._argumentType = argumentType
            
        def argumentType(self):
            return self._argumentType
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            if self._argumentType is not None:
                return pre + "typedef " + self._argumentType + " " + self._name + ";\n"
            else:
                contents = ""
                if len(self._items)!=0:
                    contents = self._items[0].format(indent+1)
                return pre + "typedef\n" + " " + contents
                
    class FunctionPointerTypedef(Typedef):
        @sealed
        def __init__(self,parentScope, functionArgument, filename, lineno):
            SymbolData.Typedef.__init__(self,parentScope, functionArgument.name(), filename, lineno)
            self._functionArgument = functionArgument
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            return pre + "typedef "+ self._functionArgument.format() + ";\n"
                
    class Macro(object):
        @sealed
        def __init__(self, name):
            self._name = name
            
        def name(self):
            return self._name
        
    class ScopedMacro(_CppEntity):
        @sealed
        def __init__(self,parentScope, name, filename, lineno):
            SymbolData._CppEntity.__init__(self, parentScope, name, filename, lineno)
            self._argument = None
            
        def setArgument(self,argument):
            self._argument = argument
            
        def format(self,indent=0):
            pre = SymbolData._indentString(indent)
            if self._argument is None:
                return pre + self._name + "\n"
            else:
                return pre + self._name + "(" + self._argument + ")\n"
            