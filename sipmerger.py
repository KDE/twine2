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

def MergeSipScope(sipsym,primaryScope,updateScope):
    """
    Updates the given primary scope using the content of the update scope.
    The primary scope typically contains extra annotations and edits which
    have been added by hand. This function updates the primary scope with
    function, class and method etc contents of the update scope while
    trying to preserve any manually added annoations etc.
    
    Keyword arguments:
    primaryScope -- A `sipsymboldata.SymbolData.Scope`
    updateScope -- A `sipsymboldata.SymbolData.Scope` object. Update information is taken from here and merged into the primary scope.
    """
    newScope = primaryScope
    oldScope = updateScope

    primaryFunctionMap = {}
    primaryClassMap = {}
    primaryNamespaceMap = {}
    primaryEnumMap = {}
    primaryTypedefMap = {}
    
    handledFunctions = set()
    
    # Index the primary scope
    for item in primaryScope:
        if isinstance(item,sipsym.Function) or isinstance(item,sipsym.Constructor) or isinstance(item,sipsym.Destructor):
            primaryFunctionMap[_MangleFunctionName(sipsym,item)] = item
        elif isinstance(item,sipsym.SipClass):
            primaryClassMap[item.fqName()] = item
        elif isinstance(item,sipsym.Namespace):
            primaryNamespaceMap[item.fqName()] = item
        elif isinstance(item,sipsym.Enum):    
            primaryEnumMap[item.fqName()] = item
        elif isinstance(item,sipsym.Typedef):
            primaryTypedefMap[item.fqName()] = item

    # Update
    for item in updateScope[:]:
        # Loop over a copy of the item because we might change the list on the fly.
        
        if isinstance(item,sipsym.Function) or isinstance(item,sipsym.Constructor) or isinstance(item,sipsym.Destructor):
            mangledName = _MangleFunctionName(sipsym,item)
            if mangledName in primaryFunctionMap:
                _MergeSipFunction(sipsym,primaryFunctionMap[mangledName],item)
                del primaryFunctionMap[mangledName]
                handledFunctions.add(mangledName)
            else:
                # New function.
                if mangledName not in handledFunctions:
                    primaryScope.append(item)
                
        elif isinstance(item,sipsym.SipClass):
            if item.fqName() in primaryClassMap:
                _MergeSipClass(sipsym,primaryClassMap[item.fqName()],item)
            else:
                # New class
                primaryScope.append(item)
                
        elif isinstance(item,sipsym.Namespace):
            if item.fqName() in primaryNamespaceMap:
                primaryNamespace = primaryNamespaceMap[item.fqName()]
                if not primaryNamespace.ignore():
                    MergeSipScope(sipsym,primaryNamespace,item)
            else:
                # New namespace
                primaryScope.append(item)
                
        elif isinstance(item,sipsym.Enum):
            if item.fqName() in primaryEnumMap:
                _MergeEnum(sipsym,primaryEnumMap[item.fqName()],item)
                del primaryEnumMap[item.fqName()]
            else:
                # New enum
                primaryScope.append(item)
        
        elif isinstance(item,sipsym.Typedef):
            # FIXME Try to be independant from Qt not hard code QFlags in.
            if "QFlags" in item.argumentType():
                if item.fqName() not in primaryTypedefMap:
                    primaryScope.append(item)
            else:
                print("Warning: Skipping typdef " +str(item))
        else:
            if not isinstance(item,sipsym.SipDirective) and not isinstance(item,sipsym.Comment):
                print("Warning: Unknown object " +str(item))
                
    # Handle any left over functions which are forced.
    for primaryFunctionName,function in primaryFunctionMap.items():
        if not function.force():
            del primaryScope[primaryScope.index(function)]

    for primaryEnumName,enum in primaryEnumMap.items():
        if not enum.force():
            del primaryScope[primaryScope.index(enum)]

def _MergeSipFunction(sipsym,primaryFunction,updateFunction):
    if updateFunction.annotations() is not None:
        annotations = set(updateFunction.annotations())
        if primaryFunction.annotations() is not None:
            annotations.update(primaryFunction.annotations())
        primaryFunction.setAnnotations(annotations)

    # Update the arguments by name.
    
    def name(item):
        if item.name() is not None and name!="": 
            return item.name()
        else:
            return "$a" + str(i)
    
    primaryArguments = {}
    i = 0
    for arg in primaryFunction.arguments():
        primaryArguments[name(arg)] = arg
        i += 1
        
    newArguments = []
    i = 0
    for updateArg in updateFunction.arguments():
        if name(updateArg) in primaryArguments:
            newArguments.append(_MergeArgument(sipsym,primaryArguments[name(updateArg)],updateArg))
        else:
            newArguments.append(_MergeArgument(sipsym,updateArg,updateArg))
        i += 1
            
    primaryFunction.setArguments(newArguments)

def _MangleFunctionName(sipsym,function):
    name = function.name()
    if isinstance(function,sipsym.Destructor):
        name = "~" + name

    name = name + '(' + \
        ','.join([arg.argumentType() for arg in function.arguments() if arg.defaultValue() is None]) + ')'

    if 'const' in function._qualifier:
        name = name + " const"
        
    return name

def _MergeArgument(sipsym,primaryArgument,updateArgument):
    resultArg = sipsym.Argument(primaryArgument.argumentType(),
                    primaryArgument.name(),
                    primaryArgument.defaultValue(),
                    primaryArgument.template(),
                    primaryArgument.defaultTypes())
    
    annotations = list(primaryArgument.annotations())
    for anno in updateArgument.annotations():
        if anno not in annotations:
            annotations.append(anno)

    resultArg.setAnnotations(annotations)
    return resultArg

def _MergeSipClass(sipsym,primaryClass,updateClass):
    annotations = list(updateClass.annotations())
    for anno in primaryClass.annotations():
        if anno not in annotations:
            annotations.append(anno)
    primaryClass.setAnnotations(annotations)
    
    MergeSipScope(sipsym,primaryClass,updateClass)
    
def _MergeEnum(sipsym,primaryEnum,updateEnum):
    annotations = list(updateEnum.annotations())
    for anno in primaryEnum.annotations():
        if anno not in annotations:
            annotations.append(anno)
    primaryEnum.setAnnotations(annotations)

    primaryEnum[:] = [sipsym.Enumerator(e.name(),e.value()) for e in updateEnum]
