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

def MergeSipScope(sipsym,oldScope,newScope):
    oldFunctionMap = {}
    oldClassMap = {}
    oldNamespaceMap = {}
    
    # Index the old scope
    for item in oldScope:
        if isinstance(item,sipsym.Function) or isinstance(item,sipsym.Constructor) or isinstance(item,sipsym.Destructor):
            oldFunctionMap[_MangleFunctionName(item)] = item
        elif isinstance(item,sipsym.SipClass):
            oldClassMap[item.fqName()] = item
        elif isinstance(item,sipsym.Namespace):
            oldNamespaceMap[item.fqName()] = item
    
    for item in newScope:
        if isinstance(item,sipsym.Function) or isinstance(item,sipsym.Constructor) or isinstance(item,sipsym.Destructor):
            mangledName = _MangleFunctionName(item)
            if mangledName in oldFunctionMap:
                _MergeSipFunction(sipsym,oldFunctionMap[mangledName],item)
        elif isinstance(item,sipsym.SipClass):
            if item.fqName() in oldClassMap:
                _MergeSipClass(sipsym,oldClassMap[item.fqName()],item)
        elif isinstance(item,sipsym.Namespace):
            if item.fqName() in oldNamespaceMap:
                MergeSipScope(sipsym,oldNamespaceMap[item.fqName()],item)
        
def _MergeSipFunction(sipsym,oldFunction,newFunction):
    newFunction.setIgnore(oldFunction.ignore())
    newFunction.setForce(oldFunction.force())
    newFunction.setBlocks(oldFunction.blocks())
    
    if oldFunction.annotations() is not None:
        annotations = set(oldFunction.annotations())
        if newFunction.annotations() is not None:
            annotations.update(newFunction.annotations())
            newFunction.setAnnotations(annotations)

    newFunction.setArguments( [_MergeArgument(sipsym,oldFunction.arguments()[i],newFunction.arguments()[i]) \
        for i in range(len(newFunction.arguments()))] )

def _MangleFunctionName(function):
    return function.name() + '(' + \
        ','.join([arg.argumentType() for arg in function.arguments() if arg.defaultValue() is None]) + ')'

def _MergeArgument(sipsym,oldArgument,newArgument):
    resultArg = sipsym.Argument(newArgument.argumentType(), newArgument.name(), newArgument.defaultValue(), newArgument.template(), newArgument.defaultTypes())
    
    annotations = list(newArgument.annotations())
    for anno in oldArgument.annotations():
        if anno not in annotations:
            annotations.append(anno)

    newArgument.setAnnotations(annotations)
    return newArgument

def _MergeSipClass(sipsym,oldClass,newClass):
    annotations = list(newClass.annotations())
    for anno in oldClass.annotations():
        if anno not in annotations:
            annotations.append(anno)

    newClass.setAnnotations(annotations)
    
    MergeSipScope(sipsym,oldClass,newClass)
    