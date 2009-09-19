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
from sealed import sealed
import os
import os.path

class ModuleGenerator(object):
    @sealed
    def __init__(self,module,cmakelists=[],ignoreHeaders=[],outputDirectory=None,
            preprocessSubstitutionMacros=[],macros=[],bareMacros=[],exportMacros=None,ignoreBases=None,
            sipImportDirs=[],sipImports=[],copyrightNotice=None,annotationRules=[]):
            
        self._module = module
        self._cmakelists = [cmakelists] if isinstance(cmakelists,str) else cmakelists
        self._ignoreHeaders = set([ignoreHeaders] if isinstance(ignoreHeaders,str) else ignoreHeaders)
        self._outputDirectory = outputDirectory
        
        self._preprocessSubstitutionMacros = preprocessSubstitutionMacros
        self._macros = macros
        self._bareMacros = bareMacros
        
        self._symbolData = cppsymboldata.SymbolData()
        self._cppParser = cppparser.CppParser()
        self._cppParser.bareMacros = self._bareMacros
        self._cppParser.macros = self._macros
        self._cppParser.preprocessorSubstitutionMacros = self._preprocessSubstitutionMacros
        
        self._cppScopeList = []

        self._transformer = cpptosiptransformer.CppToSipTransformer()
        self._transformer.setExportMacros(exportMacros)
        self._transformer.setIgnoreBaseClasses(ignoreBases)
        self._transformer.setCopyrightNotice(copyrightNotice)
        
        self._copyrightNotice = copyrightNotice
        
        self._sipImportDirs = sipImportDirs
        self._sipImports = sipImports
        
        self._sipParser = sipparser.SipParser()
        self._sipSymbolData = sipsymboldata.SymbolData()
        
        self._annotator = cpptosiptransformer.SipAnnotator()
        self._annotator.setMethodAnnotationRules(annotationRules)
        
    def run(self):
        print("Extracting header file list from CMake.")
        cppHeaderFilenameList = self.extractCmakeListsHeaders()
        
        print("Parsing Cpp headers.")
        headerScopeTuples = self._parseHeaders(cppHeaderFilenameList)
        
        print("Parsing imported Sip files.")
        self._parseImportHeaders()
        
        print("Convering header files into Sip files.")
        moduleSipScopes = self._convertCppToSip(headerScopeTuples)
        
        print("Annotating Sip files.")
        self._annotateSipScopes(moduleSipScopes)
        
        print("Computing 'Convert To Sub Class Code'.")
        cpptosiptransformer.UpdateConvertToSubClassCodeDirectives(self._sipSymbolData,moduleSipScopes,[])

        print("Sanity check.")
        cpptosiptransformer.SanityCheckSip(self._sipSymbolData,moduleSipScopes)

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
                if header not in self._ignoreHeaders:
                    filenames.append(os.path.join(dirName,header))
        return set(filenames)
        
    def _parseHeaders(self,cppHeaderFilenameList):
        headerScopeTuples = []
        
        for filename in cppHeaderFilenameList:
            with open(filename) as fhandle:
                text = fhandle.read()
            basename = os.path.basename(filename)
            scope = self._cppParser.parse(self._symbolData, text, filename=filename)
            scope.setHeaderFilename(basename)
            headerScopeTuples.append( (basename,scope) )
            #print(scope.format())
        return headerScopeTuples
    
    def _parseImportHeaders(self):
        scopes = []
        
        for sipImport in self._sipImports:
            filename = self._findSipMod(sipImport)
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
    
    def _importSipFile(self,sipFilename):
        with open(sipFilename) as fhandle:
            text = fhandle.read()
            
        scope = self._sipParser.parse(self._sipSymbolData,text,filename=sipFilename)
        
        #print("********************************************")
        #print(scope.format())
        
        modDir = os.path.dirname(sipFilename)
        
        for item in scope:
            if isinstance(item,self._sipSymbolData.SipDirective):
                if item.body().startswith("%Include"):
                    sipIncludeFilename = item.body()[len("%Include")+1:]
                    #print("body:"+sipIncludeFilename)
                    sipIncludeFullFilename = os.path.join(modDir,sipIncludeFilename)
                    if os.path.exists(sipIncludeFullFilename):
                        self._importSipFile(sipIncludeFullFilename)
                    else:
                        print("Error: Unable to find sip import '%s'. (sipImportDirs=%s" % (sipModName,repr(self._sipImportDirs)))
                    
        return scope
    
    def _convertCppToSip(self,headerScopeTuples):
        sipScopes = []
        for headerName,cppScope in headerScopeTuples:
            sipscope = self._transformer.convert(cppScope,self._sipSymbolData)
            sipScopes.append(sipscope)
        return sipScopes
        
    def _annotateSipScopes(self,moduleSipScopes):
        for scope in moduleSipScopes:
            self._annotator.applyRules(scope)
        
    def _convertHeaderNameToSip(self,headerName):
        return headerName[:-2]+".sip"
        
    def _writeScopes(self,moduleSipScopes):
        for scope in moduleSipScopes:
            fullPath = os.path.join(self._outputDirectory,self._convertHeaderNameToSip(scope.headerFilename()))
            with open(fullPath,'w') as fhandle:
                fhandle.write(scope.format())
                
    def _writeIndexSip(self,scopes):
        moduleName = self._module
        if '.' in self._module:
            moduleName = self._module[self._module.rfind('.')+1:]
        fullFilename = os.path.join(self._outputDirectory,moduleName) + "mod.sip"
        with open(fullFilename,'w') as fhandle:
            fhandle.write(self._indexSip(scopes))
        
    def _indexSip(self,scopes):
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
        
        for scope in scopes:
            accu.append("%Include ")
            accu.append(self._convertHeaderNameToSip(scope.headerFilename()))
            accu.append("\n")
        
        return ''.join(accu)

def AnnotationRule(methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations):
    return cpptosiptransformer.MethodAnnotationRule(methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations)
