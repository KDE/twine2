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

import cmake
import cppparser
import cppsymboldata
import sipparser
import sipsymboldata
import cpptosiptransformer
import sipmerger
from sealed import sealed
import sys
import os
import os.path

class ModuleGenerator(object):
    @sealed
    def __init__(self,module,cmakelists=[],ignoreHeaders=[],noUpdateSip=[],outputDirectory=None,
            preprocessorValues=[],preprocessSubstitutionMacros=[],macros=[],bareMacros=[],exportMacros=None,
            ignoreBases=None,noCTSCC=[],sipImportDirs=[],sipImports=[],copyrightNotice=None,annotationRules=[]):
            
        self._module = module
        self._cmakelists = [cmakelists] if isinstance(cmakelists,str) else cmakelists
        self._ignoreHeaders = set([ignoreHeaders] if isinstance(ignoreHeaders,str) else ignoreHeaders)
        self._noUpdateSip = noUpdateSip
        self._outputDirectory = outputDirectory
        
        self._preprocessorValues = preprocessorValues
        self._preprocessSubstitutionMacros = preprocessSubstitutionMacros
        self._macros = macros
        self._bareMacros = bareMacros
        
        self._symbolData = cppsymboldata.SymbolData()
        self._cppParser = cppparser.CppParser()
        self._cppParser.preprocessorValues = self._preprocessorValues
        self._cppParser.bareMacros = self._bareMacros
        self._cppParser.macros = self._macros
        self._cppParser.preprocessorSubstitutionMacros = self._preprocessSubstitutionMacros
        
        self._cppScopeList = []

        self._transformer = cpptosiptransformer.CppToSipTransformer()
        self._transformer.setExportMacros(exportMacros)
        self._transformer.setIgnoreBaseClasses(ignoreBases)
        self._transformer.setCopyrightNotice(copyrightNotice)
        self._noCTSCC = noCTSCC
        
        self._copyrightNotice = copyrightNotice
        
        self._sipImportDirs = sipImportDirs
        self._sipImports = sipImports
        
        self._sipParser = sipparser.SipParser()
        self._sipSymbolData = sipsymboldata.SymbolData()
        
        self._annotator = cpptosiptransformer.SipAnnotator()
        self._annotator.setMethodAnnotationRules(annotationRules)
        
    def run(self):
        print("Extracting header file list from CMake:")
        cppHeaderFilenameSet = self.extractCmakeListsHeaders()
        cppHeaderFilenameList = list(cppHeaderFilenameSet)
        cppHeaderFilenameList.sort()
        for filename in cppHeaderFilenameList:
            print("    Found %s" % (filename,))
        
        print("\nParsing Cpp headers:")
        headerScopeTuples = self._parseHeaders(cppHeaderFilenameList)
        
        print("\nParsing imported Sip files:")
        self._parseImportedSip()
        
        print("\nConverting header files into Sip files.")
        moduleSipScopes = self._convertCppToSip(headerScopeTuples)
        
        print("\nExpanding class names:")
        for scope in moduleSipScopes:
            cpptosiptransformer.ExpandClassNames(self._sipSymbolData,scope)

        print("\nAnnotating Sip files.")
        self._annotateSipScopes(moduleSipScopes)
        
        _indexFilename = self._indexFilename()
        if os.path.exists(_indexFilename):
            print("\nParsing previous Sip files.")
            moduleSipScopes = self._updateScopes(moduleSipScopes)
        else:
            print("(%s not found. Skipping merge with previous sip files.)" % (_indexFilename,))
            
        print("\n")
        
        print("Computing 'Convert To Sub Class Code'.")
        cpptosiptransformer.UpdateConvertToSubClassCodeDirectives(self._sipSymbolData,moduleSipScopes,self._noCTSCC)

        #print("Sanity check.")
        #cpptosiptransformer.SanityCheckSip(self._sipSymbolData,moduleSipScopes)
        
        print("Writing Sip files.")
        if self._outputDirectory is not None:

            if os.path.exists(self._outputDirectory) and not os.path.isdir(self._outputDirectory):
                print("Error: Output directory '%s' is not a directory.")
            else:
                if not os.path.exists(self._outputDirectory):
                    os.mkdir(self._outputDirectory)
                self._writeScopes(moduleSipScopes)
                self._writeIndexSip(moduleSipScopes)
        else:        
            print("Warning: Skipping writing because no output directory was specified.")
        
        #for scope in moduleSipScopes:
        #    print(scope.format())
        print("Done.")
        
    def extractCmakeListsHeaders(self):
        filenames = []
        for cmakeFilename in self._cmakelists:
            dirName = os.path.dirname(cmakeFilename)
            for header in cmake.ExtractInstallFiles(cmakeFilename):
                if os.path.basename(header) not in self._ignoreHeaders:
                    filenames.append(os.path.join(dirName,header))
        return set(filenames)
        
    def _parseHeaders(self,cppHeaderFilenameList):
        headerScopeTuples = []
        
        for filename in cppHeaderFilenameList:
            print("    Parsing %s" % (filename,))
            with open(filename) as fhandle:
                text = fhandle.read()
            basename = os.path.basename(filename)
            scope = self._cppParser.parse(self._symbolData, text, filename=filename, debugLevel=0)
            scope.setHeaderFilename(basename)
            headerScopeTuples.append( (basename,scope) )
            #print(scope.format())
        return headerScopeTuples
    
    def _parseImportedSip(self):
        scopes = []
        
        for sipImport in self._sipImports:
            filename = self._findSipMod(sipImport)
            if filename is None:
                raise SystemExit
            print("    Parsing %s" % (filename,))
            scopes.append(self._importSipFile(filename))
        return scopes
        
    def _findSipMod(self,sipModName):
        for sipImportDir in self._sipImportDirs:
            filename = os.path.join(sipImportDir,sipModName)
            if os.path.exists(filename):
                return filename
        else:
            print("Error: Unable to find sip import '%s'. (sipImportDirs=%s" % (sipModName,repr(self._sipImportDirs)))
        return None
    
    def _importSipFile(self,sipFilename,noUpdateSip=[]):
        with open(sipFilename) as fhandle:
            text = fhandle.read()

        scope = self._sipParser.parse(self._sipSymbolData,text,filename=sipFilename,debugLevel=0)
        
        # Figure out the Cpp header file name.
        def findAll(scope,matchType):
            result = []
            for item in scope:
                if isinstance(item,matchType):
                    result.append(item)
                if isinstance(item,self._sipSymbolData.SipClass) or isinstance(item,self._sipSymbolData.Namespace):
                    result.extend(findAll(item,matchType))
            return result
        
        def extractHeader(directives,directiveName):
            for directive in directives:
                if directive.name()==directiveName and directive.body() is not None:
                    for line in directive.body().split('\n'):
                        if line.startswith("#include <"):
                            return line[10:-1]

        directives = findAll(scope,self._sipSymbolData.SipDirective)
        scope.setHeaderFilename(extractHeader(directives,"%TypeHeaderCode") \
            or extractHeader(directives,"%ModuleHeaderCode") \
            or sipFilename)

        scopeList = [scope]
        
        #print("********************************************")
        #print(scope.format())
        
        modDir = os.path.dirname(sipFilename)
        
        for item in scope:
            if isinstance(item,self._sipSymbolData.SipDirective):
                if item.body().startswith("%Include"):
                    sipIncludeFilename = item.body()[len("%Include")+1:]
                    if sipIncludeFilename not in noUpdateSip:
                        sipIncludeFullFilename = os.path.join(modDir,sipIncludeFilename)
                        if os.path.exists(sipIncludeFullFilename):
                            scopeList.extend(self._importSipFile(sipIncludeFullFilename))
                        else:
                            print("Error: Unable to find sip import '%s'. (sipImportDirs=%s" % (sipModName,repr(self._sipImportDirs)))
                    
        return scopeList
    
    def _convertCppToSip(self,headerScopeTuples):
        sipScopes = []
        for headerName,cppScope in headerScopeTuples:
            print("    Converting %s" % (headerName,))
            sipscope = self._transformer.convert(cppScope,self._sipSymbolData)
            sipScopes.append(sipscope)
        return sipScopes
        
    def _annotateSipScopes(self,moduleSipScopes):
        for scope in moduleSipScopes:
            self._annotator.applyRules(scope)
        
    def _convertHeaderNameToSip(self,headerName):
        filename = os.path.basename(headerName)
        if filename.endswith(".h"):
            return filename[:-2]+".sip"
        return filename
        
    def _writeScopes(self,moduleSipScopes):
        for scope in moduleSipScopes:
            fullPath = os.path.join(self._outputDirectory,self._convertHeaderNameToSip(scope.headerFilename()))
            with open(fullPath,'w') as fhandle:
                fhandle.write(scope.format())
                
    def _writeIndexSip(self,scopes):
        moduleName = self._module
        if '.' in self._module:
            moduleName = self._module[self._module.rfind('.')+1:]
        
        indexFilename = self._indexFilename()
        with open(self._indexFilename(),'w') as fhandle:
            fhandle.write(self._indexSip( [s for s in scopes if s.headerFilename()!=indexFilename] ))
            
    def _indexFilename(self):
        module = self._module
        if '.' in module:
            module = module.rpartition('.')[2]
        return os.path.join(self._outputDirectory,module) + "mod.sip"
        
    def _updateScopes(self,updateSipScopes):
        previousSipScopes = self._importSipFile(self._indexFilename(),self._noUpdateSip)
        
        # Match updateSipScopes
        updateSipMap = {}
        for scope in updateSipScopes:
            #print("header sip name: " + self._convertHeaderNameToSip(scope.headerFilename()))
            updateSipMap[self._convertHeaderNameToSip(scope.headerFilename())] = scope
            
        for scope in previousSipScopes:
            filename = self._convertHeaderNameToSip(scope.headerFilename())
            previousScope = updateSipMap.get(filename,None)
            if previousScope is not None:
                print("    Merging %s" % (filename,))
                sipmerger.MergeSipScope(self._sipSymbolData,scope,updateSipMap[filename])
                self._sipSymbolData.removeScope(updateSipMap[filename])
                del updateSipMap[filename]
            else:
                print("    (Missing header file to match %s. Skipping merge.)" % (filename,) )
            
        for key in updateSipMap.iterkeys():
            print("    Adding new header "+key)
            previousSipScopes.append(updateSipMap[key])
            
        return previousSipScopes
        
    def _indexSip(self,scopes):
        def key(x): return x.headerFilename()
        scopes.sort(key=key)
        
        accu = []
        
        if self._copyrightNotice is not None:
            accu.append(self._copyrightNotice)
        
        accu.append("\n%Module ")
        accu.append(self._module)
        accu.append("\n\n")
        
        accu.append("%ModuleHeaderCode\n")
        accu.append("#pragma GCC visibility push(default)\n")
        accu.append("%End\n\n")
        
        # %Import
        for sipImport in self._sipImports:
            accu.append("%Import ")
            accu.append(sipImport)
            accu.append("\n")
        accu.append("\n")
        
        for sipFile in self._noUpdateSip:
            accu.append("%Include ")
            accu.append(sipFile)
            accu.append("\n")
        
        for scope in scopes:
            accu.append("%Include ")
            accu.append(self._convertHeaderNameToSip(scope.headerFilename()))
            accu.append("\n")
        
        return ''.join(accu)

def AnnotationRule(methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations):
    return cpptosiptransformer.MethodAnnotationRule(methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations)

def PySlotRule(className=None,namespaceName=None,arg1Name=None,arg2Name=None):
    return cpptosiptransformer.PySlotRule(className,namespaceName,arg1Name,arg2Name)
