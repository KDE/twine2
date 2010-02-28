# -*- coding: utf-8 -*-
#     Copyright 2009-2010 Simon Edwards <simon@simonzone.com>
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

from argvalidate import accepts,returns,one_of
import types
from sealed import sealed
import cmake
import cpplexer
import cppparser
import cppsymboldata
import sipparser
import sipsymboldata
import cpptosiptransformer
import sipmerger
import os
import os.path
from reducetxt import Reduce

reducer = Reduce()

class ModuleGenerator(object):
    @sealed
    def __init__(self,module,cmakelists=[],ignoreHeaders=[],noUpdateSip=[],outputDirectory=None,
            preprocessorValues=[],preprocessSubstitutionMacros=[],macros=[],bareMacros=[],exportMacros=None,
            ignoreBases=None,noCTSCC=[],sipImportDirs=[],sipImports=[],copyrightNotice=None,annotationRules=[],
            docsOutputDirectory=None,mainDocs=None,filenameMappingFunction=None,cppHeaderMappingFunction=None):
            
        self._module = module
        self._cmakelists = [cmakelists] if isinstance(cmakelists,str) else cmakelists
        self._ignoreHeaders = set([ignoreHeaders] if isinstance(ignoreHeaders,str) else ignoreHeaders)
        self._noUpdateSip = noUpdateSip
        self._outputDirectory = outputDirectory
        
        self._preprocessorValues = preprocessorValues
        self._preprocessSubstitutionMacros = preprocessSubstitutionMacros
        self._macros = macros
        self._bareMacros = bareMacros

        self._filenameMappingFunction = filenameMappingFunction
        self._cppHeaderMappingFunction = cppHeaderMappingFunction

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
        
        self._docsOutputDirectory = docsOutputDirectory
        self._mainDocs = mainDocs
        
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
        #return
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

            if self._cppHeaderMappingFunction is not None:
                basename = self._cppHeaderMappingFunction(self,filename)
            else:
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
    
    def _importSipFile(self,sipFilename,noUpdateSip=[],module=None):
        with open(sipFilename) as fhandle:
            text = fhandle.read()

        scope = self._sipParser.parse(self._sipSymbolData,text,filename=sipFilename,debugLevel=0)
        
        # Figure out the Cpp header file name.
        def extractHeader(directives,directiveName):
            for directive in directives:
                if directive.name()==directiveName and directive.body() is not None:
                    for line in directive.body().split('\n'):
                        if line.startswith("#include <"):
                            return line[10:-1]

        directives = self._findAllInstance(scope,self._sipSymbolData.SipDirective)
        scope.setHeaderFilename(extractHeader(directives,"%TypeHeaderCode") \
            or extractHeader(directives,"%ModuleHeaderCode") \
            or sipFilename)
        
        # Set the correct module name
        for item in scope:
            if isinstance(item,self._sipSymbolData.SipDirective):
                if item.name()=="Module":
                    module = item.body().split(' ')[1]
                    break
        scope.setModule(module)
        
        print(sipFilename + " -> " + scope.headerFilename())
        
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
                            scopeList.extend(self._importSipFile(sipIncludeFullFilename,module=module))
                        else:
                            print("Error: Unable to find sip import '%s'. (sipImportDirs=%s" % (sipIncludeFilename,repr(self._sipImportDirs)))
                    
        return scopeList
        
    def _findAllInstance(self,scope,matchType):
        result = []
        for item in scope:
            if isinstance(item,matchType):
                result.append(item)
            if isinstance(item,self._sipSymbolData.SipClass) or isinstance(item,self._sipSymbolData.Namespace):
                result.extend(self._findAllInstance(item,matchType))
        return result

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
        if self._filenameMappingFunction is not None:
            return self._filenameMappingFunction(self,headerName)

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

    def docs(self):
        print("Extracting header file list from CMake:")
        cppHeaderFilenameSet = self.extractCmakeListsHeaders()
        cppHeaderFilenameList = list(cppHeaderFilenameSet)
        cppHeaderFilenameList.sort()
        for filename in cppHeaderFilenameList:
            print("    Found %s" % (filename,))
        
        print("\nParsing Cpp headers:")
        headerScopeTuples = self._parseHeaders(cppHeaderFilenameList)
        cppScopes = [ x[1] for x in headerScopeTuples]

        print("\nParsing imported Sip files:")
        self._parseImportedSip()
        
        print("\nParsing module files:")
        previousSipScopes = self._importSipFile(self._indexFilename(),self._noUpdateSip)
        
        print("\nWriting index page:")
        self.writeModuleIndexPage(previousSipScopes)
        
        print("\nWriting class pages:")
        subclassMapping = BuildSubclassMap(previousSipScopes,self._sipSymbolData)
        #print(repr(subclassMapping))
        
        # Write out the
        def writeScopeDocs(scope):
            for item in scope:
                if isinstance(item,self._sipSymbolData.SipClass):
                    self.writeClassDoc(item,subclassMapping)
                    writeScopeDocs(item)
                elif isinstance(item,self._sipSymbolData.Namespace):
                    writeScopeDocs(item)
        for scope in previousSipScopes:
            writeScopeDocs(scope)

        print("\nWriting namespace pages:")
        self.writeNamespaces(previousSipScopes,cppScopes)
        return previousSipScopes

    @accepts(sipsymboldata.SymbolData.SipClass, dict)
    def writeClassDoc(self, sipClass, subclassMapping):
        classComment = ""
        cppClass = None
        try:
            cppClass = self._symbolData.lookupType(sipClass.fqName(),sipClass)
            
            print("\nHit " + sipClass.fqName())
            print("parent "+repr(cppClass.parentScope()))
            
            parentScope = cppClass.parentScope()
            for item in parentScope:
                if isinstance(item,self._symbolData.Comment):
                    classComment = item.value()
                    #print("classComment:"+classComment)
                if item is cppClass:
                    break
            
        except KeyError:
            print("Unable to find Cpp class while writing class docs.")

        self.writeClassPage(sipClass,subclassMapping,cppClass,classComment)

    @accepts(sipsymboldata.SymbolData.Entity)
    @returns(str)
    def commentMapKey(self, item):
        if isinstance(item, (self._sipSymbolData.Constructor, self._symbolData.Constructor)):
            argNames = [(x.name() if x.name() is not None else "") for x in item.arguments()]
            key = item.name() + "|" + '|'.join(argNames)
        else:
            key = item.name()
        return key

    @accepts(sipsymboldata.SymbolData.CppClass)
    @returns(dict)
    def buildCommentMap(self,cppClass):
        lastComment = None
        commentMap = {}

        for item in cppClass:
            if isinstance(item,self._symbolData.Comment):
                lastComment = item.value()
            elif lastComment is not None:
                if isinstance(item, (self._symbolData.Function,self._symbolData.Enum) ):
                    commentMap[self.commentMapKey(item)] = lastComment
                    lastComment = None
        return commentMap
            
    @accepts(sipsymboldata.SymbolData.SipClass, dict, one_of(sipsymboldata.SymbolData.CppClass,types.NoneType), str)
    def writeClassPage(self,sipClass,subclassMapping,cppClass,classComment):
        def nameKey(a): return a.name()
        enumList = [item for item in sipClass if isinstance(item,self._sipSymbolData.Enum) and not item.ignore()]
        enumList.sort(key=nameKey)
        
        methodList = [item for item in sipClass if isinstance(item,self._sipSymbolData.Function) and not item.ignore()]
        methodList.sort(key=nameKey)
        constructorList = [item for item in sipClass if isinstance(item,self._sipSymbolData.Constructor) and not item.ignore()]
        constructorList.extend(methodList)
        methodList = constructorList
        
        classList = [item for item in sipClass if isinstance(item,self._sipSymbolData.SipClass) and not item.ignore()]
        classList.sort(key=nameKey)
        
        variableList = [item for item in sipClass if isinstance(item,self._sipSymbolData.Variable) and not item.ignore()]
        variableList.sort(key=nameKey)

        commentMap = self.buildCommentMap(cppClass) if cppClass is not None else {}

        #if cls in self.flagged:
        #    flags = self.flagged [cls]
        #else:
        #    flags = None
        
        # create class page and add header
        className = sipClass.fqPythonName()    # FIXME fqn required plus the python name.

        page = open(os.path.join(self._docsOutputDirectory, "%s.html" % className), 'w')
        page.write(htmlHeader % {'title': className, 'path': '../'})
        
        if isSipClassAbstract(sipClass):
            abstract = """<dl class="abstract" compact><dt><b>Abstract class:</b></dt>
<dd>This class can be used as a base class for new classes, but can not be instantiated directly.</dd></dl>"""
        else:
            abstract = ''
        # &#x2192;  arrow
        if len(sipClass.bases())!=0:
            bases = []
            for base in sipClass.bases():
                try:
                    baseClass = self._sipSymbolData.lookupType(base,sipClass)
                except KeyError:
                    baseClass = None
                if baseClass is not None:
                    try:
                        if isinstance(baseClass,self._sipSymbolData.Typedef):
                            classHierarchy = self._sipSymbolData.lookupType(baseClass.argumentType(),baseClass).classHierarchy()
                        else:
                            classHierarchy = baseClass.classHierarchy()
                    except KeyError:
                        print("KeyError: Look up error on '"+baseClass.name()+"'")
                        classHierarchy = []

                    bases.append(' &#x2192; '.join([self.formatType(x.fqPythonName(),sipClass) for x in classHierarchy]))
            
            baseClasses = 'Inherits: '+ (','.join(bases)) + '<br />'
        else:
            baseClasses = ''
        
        subClassSet = subclassMapping.get(sipClass,None)
        if subClassSet is not None:
            subClassList = list(subClassSet)
            subClassList.sort()
            subClasses = 'Subclasses: ' + (', '.join ( [self.formatType(x.fqName(),sipClass) for x in subClassList] )) + '<br />'
        else:
            subClasses = ''
        
        namespace = "Namespace: " + sipClass.fqPythonName() + "<br />" if sipClass.fqPythonName()!=sipClass.name() else ""
        
        page.write (classHeader %
            {'classname': pyName(sipClass),
            'abstract': abstract,
            'modulename': self._module,
            'namespace': namespace,
            'baseclasses': baseClasses,
            'subclasses': subClasses,
            'description': self.formatDoxygen(classComment)} )
            
        page.write("""<table border="0" cellpadding="0" cellspacing="0">""")
        
        # enums
        page.write(self.writeEnums(enumList))
        
        page.write(self.writeVariables(variableList))
        
        count = [0]
        def SignalFilter(obj):
            if obj.access() is self._sipSymbolData.ACCESS_SIGNALS:
                count[0] += 1
                return True
            else:
                return False
        s = self.writeMethodIndex(methodList, SignalFilter, "Signals", False)
        if count[0]!=0:
            page.write(s)
        
        count = [0]
        def MethodFilter(obj):
            if 'static' not in obj.qualifier():
                count[0] += 1
                return True
            else:
                return False
        s = self.writeMethodIndex(methodList, MethodFilter, "Methods")
        if count[0]!=0:
            page.write(s)
        
        count = [0]
        def StaticFilter(obj):
            if 'static' in obj.qualifier():
                count[0] += 1
                return True
            else:
                return False
        s = self.writeMethodIndex(methodList, StaticFilter, "Static Methods", False)
        if count[0]!=0:
            page.write(s)

        page.write("</table>\n")
        
        # methods
        self.writeMethodDetails(page, methodList, commentMap)
        
        # variables
        self.writeVariableDetails(page, variableList, commentMap)
        
        # enum detail
        self.writeEnumDetail(page, enumList, commentMap)#, flags)
    
        # footer
        page.write(htmlFooter % {'path': '../'})
        page.close()
        
    @accepts(list, types.FunctionType, str, useSelf=bool)
    @returns(str)
    def writeMethodIndex(self, methodList, methodFilter, title, useSelf=True):
        result = []
        result.append("""<tr><td colspan="2"><br><h2>""")
        result.append(title)
        result.append("""</h2></td></tr>\n""")
        
        for obj in methodList:
            if not methodFilter(obj):
                continue
                
            retList = []
            if obj.return_():
                retList.append(self.formatArgument(obj.return_(),obj))
                
            for arg in obj.arguments():
                if 'Out' in arg.annotations():
                    if arg.name():
                        retList.append ('%s %s' % (self.formatType(arg.argumentType(),obj), arg.name()))
                    else:
                        retList.append (self.formatType(arg.argumentType(),obj))
            
            if retList:
                ret = ', '.join ( (item for item in retList if item!='') )
            else:
                ret = ''
                
#            param = ''
#            if 'pure' in obj.attributes.functionQualifier:
#                param += '<b style="color : #00aa00">pure virtual</b>'
#            if obj.ignore or obj.access == 'private':
#                param = '<i style="color : #aa0000">Not implemented</i>'
#            
#            if param != '':
#                print(obj.name + "~> "+param)
                
            if isinstance(obj, self._sipSymbolData.Constructor):
                memname = "__init__"
                ret = ""
            else:
                memname = pyName(obj)
            memname = '<a class="el" href="#' + linkId(obj) + '">' + memname + '</a>'
                
            result.append('<tr><td class="memItemLeft" nowrap align="right" valign="top">' + ret +'&nbsp;</td><td class="memItemRight" valign="bottom">' + memname + ' (')
            
            comma = ""
            if useSelf:
                result.append('self')
                if len(obj.arguments())!=0:
                    comma = ", "

            i = 0
            for a in obj.arguments():
                if 'In' in a.annotations() or not 'Out' in a.annotations():
                    paramtype = self.formatType(a.argumentType(),obj)
                    paramname = a.name()
                    if paramname is None:
                        paramname = 'a%i' % i
                    if a.defaultValue() is not None:
                        paramname += "=" + a.defaultValue().replace ('::', '.')
                        
                    comma = ", "
                
                    result.append(comma + paramtype + " " + paramname)
                    i += 1
            result.append(')</td></tr>\n')
        return "".join(result)
        
    @accepts(file, list, dict, title=str, functions=bool)
    def writeMethodDetails(self, page, methodList, commentMap, title="Method Documentation", functions=False):
        if not methodList:
            return
            
        page.write('<hr><h2>' + title + '</h2>')
        for obj in methodList:
            comment = commentMap.setdefault(self.commentMapKey(obj),"")
            self.writeMethodDetail(page, obj, comment, function=functions)
        
    @accepts(file, one_of(sipsymboldata.SymbolData.Function,sipsymboldata.SymbolData.Constructor), str, function=bool)
    def writeMethodDetail(self, page, obj, comment, function=False):
        retList = []
        if obj.return_():
            retList.append(self.formatArgument(obj.return_(),obj))
            
        for arg in obj.arguments():
            if 'Out' in arg.annotations():
                if arg.name():
                    retList.append ('%s %s' % (self.formatArgument(arg,obj), arg.name()))
                else:
                    retList.append (self.formatArgument(arg,obj))
        
        if retList:
            ret = ', '.join ( (item for item in retList if item!='') )
        else:
            ret = ''

#            param = ''
#            if obj.ignore or obj.access == 'private':
#                param = '<i style="color : #aa0000">Not implemented</i>'
        #i = 0
        #for arg in obj.arguments:
        #    if not arg.name():
        #        arg.name = 'a%i' % i
        #        i += 1
            
        args = """<a class="anchor" name=\"""" + linkId(obj) + """"></a>
<div class="memitem">
<div class="memproto">
<table class="memname">"""
        if isinstance(obj, self._sipSymbolData.Constructor):
            memname = "__init__"
            ret = ""
        else:
            memname = ret + " " + pyName(obj)
        
        filteredArguments = [a for a in obj.arguments() if 'In' in a.annotations() or not 'Out' in a.annotations()]
        
        if not filteredArguments:
            selfarg = '<em>self</em>&nbsp;' if 'static' not in obj.qualifier() and not function else ''
            args += """<tr>
<td class="memname">%s</td>
<td>(</td>
<td class="paramtype">&nbsp;</td>
<td class="paramname">%s)</td>
<td width="100%%"> </td>
</tr>
""" % (memname,selfarg)
        
        else:
            bracket = "("
            if not function and 'static' not in obj.qualifier():
                args += """<tr>
<td class="memname">%s</td>
<td>%s</td>
<td class="paramtype">&nbsp;<em>self</em>, </td>
<td class="paramname"></td>
</tr>""" % (memname,bracket)
                memname = ""
                bracket = ""
            
            i = 0
            for a in filteredArguments:
                paramtype = self.formatArgument(a,obj)
                paramname = a.name()
                if paramname is None:
                    paramname = 'a%i' % i
                if a.defaultValue() is not None:
                    paramname += "=" + a.defaultValue().replace ('::', '.')
                    
                comma = ", " if a is not filteredArguments[-1] else ""
            
                args += """<tr>
<td class="memname">%s</td>
<td>%s</td>
<td class="paramtype">%s&nbsp;</td>
<td class="paramname"><em>%s</em>%s</td>
</tr>
""" % (memname,bracket,paramtype,paramname,comma)
                memname = ""
                bracket = ""
                i += 1
            args += """<tr>
<td></td>
<td>)</td>
<td></td>
<td></td>
<td width="100%"> </td>
</tr>"""
        args += """</table>
</div>
"""
        page.write(args)
    
        page.write('<div class="memdoc">')
        if 'pure' in obj.qualifier():
            page.write("""<dl compact><dt><b>Abstract method:</b></dt><dd>""")
            page.write("This method is abstract and can be overridden but not called directly.")
            page.write("""</dd></dl>""")

        page.write(self.formatDoxygen(comment))
        if obj.access() is self._sipSymbolData.ACCESS_SIGNALS:
            args = [arg.argumentType() for arg in obj.arguments()]
            page.write("""<dl compact><dt><b>Signal syntax:</b></dt><dd>""")
            page.write("""<code>QObject.connect(source, SIGNAL("%s(%s)"), target_slot)</code>""" % (pyName(obj), ', '.join (args)))
            page.write("""</dd></dl>""")
        
        page.write('</div></div>')

    @accepts(list)
    @returns(str)
    def writeEnums(self, enumList): #:, flags = None):
        if len(enumList)==0:
            return ""
            
        result = []
        result.append("""<tr><td colspan="2"><br><h2>Enumerations</h2></td></tr>\n""")

        for obj in enumList:
            typeSafe = None
            if not obj.name():
                objName = "&lt;anonymous&gt;"
            else:
                #if flags and obj.name() in flags:
                #    typeSafe = flags [obj.name()]
                objName = obj.name()
           
            result.append('<tr><td class="memItemLeft" nowrap align="right" valign="top"><a class="el" href="#' + linkId(obj) + '">' + objName +'</a>&nbsp;</td><td class="memItemRight" valign="bottom">{&nbsp;')
               
            result.append(", ".join( [x.name() for x in obj] ))
                
            if typeSafe:
                result.append('&nbsp;}<br><i>Typesafe wrapper:</i> %s</td></tr>\n' % (typeSafe))
            else:
                result.append("&nbsp;}</td></tr>\n")

        return "".join(result)

    @accepts(list)
    @returns(str)
    def writeVariables(self, variableList):
        if not variableList:
            return ""
        result = []
        result.append("""<tr><td colspan="2"><br><h2>""")
        result.append("Attributes")
        result.append("""</h2></td></tr>\n""")
        
        for obj in variableList:
            result.append('<tr><td class="memItemLeft" nowrap align="right" valign="top">' + self.formatArgument(obj.argument(),obj) + '&nbsp;</td><td class="memItemRight" valign="bottom"><a class="el" href="#var' + linkId(obj) + '">' + obj.name() +'</a></td></tr>')
        return "".join(result)

    @accepts(file,list,dict)
    def writeVariableDetails(self, page, variableList, commentMap):
        if not variableList:
            return
        
        page.write('<hr><h2>Attribute Documentation</h2>')

        for obj in variableList:
            page.write("""<a class="anchor" name="var""" + linkId(obj) + """"></a>
<div class="memitem">
<div class="memproto">
<table class="memname">
<tr><td class="memname">""")
            page.write(self.formatArgument(obj.argument(),obj))
            page.write(" ")
            page.write(pyName(obj))
            page.write("""</td>
</tr>
</table>
</div>
<div class="memdoc">""")
            page.write(self.formatDoxygen(commentMap.setdefault(self.commentMapKey(obj),"")))
            page.write("""</div></div><p>""")            

    @accepts(file,list,dict)
    def writeEnumDetail(self, page, enumList, commentMap): #flags = None):
        if not enumList:
            return
            
        page.write('<hr><h2>Enumeration Documentation</h2>')
        
        for obj in enumList:
            page.write("""<a class="anchor" name=\"""" + linkId(obj) + """"></a>
<div class="memitem">
<div class="memproto">
<table class="memname">
<tr><td class="memname">""")
            typeSafe = None
            if not obj.name():
                name = 'anonymous'
            else:
                #if flags and obj.name() in flags:
                #    typeSafe = flags [obj.name()]
                name = obj.name()
            page.write(name)
            page.write("""</td>
</tr>
</table>
</div>
<div class="memdoc">""")
            page.write(self.formatDoxygen(commentMap.setdefault(self.commentMapKey(obj),"")))
            
            if typeSafe:
                page.write("""<dl compact><dt><b>Note:</b></dt><dd>""")
                page.write("It is necessary to wrap members of this enumeration in a <code>" + typeSafe + "</code> instance when passing them to a method as group of flags. ")
                if len(obj.enumerators())>=2:
                    page.write("For example: <code>" + typeSafe + "( " + obj[0].name() + " | " + obj[1].name() + ")</code>")
                page.write("""</dd></dl>""")
                
            page.write("""<dl compact><dt><b>Enumerator: </b></dt><dd>
<table border="0" cellspacing="2" cellpadding="0">""")

            if obj.name() is not None:
                try:
                    cppEnum = self._symbolData.lookupType(obj.name(),obj)
                    print("Enum type is :" + repr(cppEnum));
                    obj = cppEnum
                except KeyError:
                    print("Couldn't find enum:"+obj.name())

            for e in obj:
                if isinstance(e,self._symbolData.Enumerator):
                    #docLine = self.formatDoxygen(e.doc).strip().replace('/', ' ')
                    docLine = ''
                    if e.value():
                        val = '=&nbsp;' + str(e.value())
                    else:
                        val = ''

                    page.write('<tr><td valign="top"><em>')
                    page.write(e.name())
                    page.write('</em>&nbsp;')
                    page.write(val)
                    page.write(docLine)
                    page.write('</td><td>')
            page.write("""</table>
</dl>
</div></div><p>""")

    @accepts(list)
    def writeModuleIndexPage(self,sipScopes):
        #nsNames = self.namespaces.keys()
        #nsNames.sort()
        nsList = list(set( (item.name() for scope in sipScopes for item in scope if isinstance(item,self._sipSymbolData.Namespace) and not item.ignore()) ))
        nsList.append('global')
        nsList.sort()
        
        if self._mainDocs:
            mainDocs = FetchDocs(self._mainDocs)
        else:
            mainDocs = ''

        page = open(os.path.join(self._docsOutputDirectory, 'index.html'), 'w')
        page.write(htmlHeader % {'title': ('Module %s' % self._module), 'path': '../'})
        page.write("<h1>%s Module</h1>\n" % self._module)
        page.write("<hr>")
        page.write(self.formatDoxygen(mainDocs))

        self.writeNSNamespacesIndex(page, nsList)
        
        classList = []
        for scope in sipScopes:
            classList.extend(self._findAllInstance(scope,self._sipSymbolData.SipClass))
        #print(repr(classList))
        classList = list( set (class_ for class_ in classList if not class_.ignore()) )
        def nameKey(a): return a.name()
        classList.sort(key=nameKey)
        
        self.writeNSClassIndex(page, classList)

        page.write(htmlFooter % {'path': '../'})
        page.close()

    @accepts(list,list)
    def writeNamespaces(self,sipScopes,cppScopes):
        # Figure out what namespace we have.
        namespaceCollector = {} # namespace FQN -> list of namespace objects
        for scope in sipScopes:
            for item in scope:
                if isinstance(item, self._sipSymbolData.Namespace):
                    nsList = namespaceCollector.setdefault(item.fqName(),[])
                    nsList.append(item)

        print("nsList: " + repr(nsList))

        self.writeNamespacePage("global",sipScopes,cppScopes)

        for fqName,ns in namespaceCollector.items():
            self.writeNamespacePage(fqName,ns,cppScopes)

    @accepts(str,list,list)
    def writeNamespacePage(self,nsName,nsList,cppScopes):
#        print(repr(cppScopes))
        # create namespace page and add header
        nspage = open(os.path.join(self._docsOutputDirectory, "%s.html" % nsName), 'w')
        nspage.write(htmlHeader % {'title': nsName, 'path': '../'})

        importcode = "from %s.%s import *" % (self._module,nsName)
        if nsName=='global':
            importcode = "from " + self._module + " import *"

        description = ""
        if nsName!='global':
            for cppNS in self._symbolData.lookupNamespace(nsName):
                lastComment = None
                for item in cppNS.parentScope():
                    if isinstance(item,self._symbolData.Comment):
                        lastComment = item.value()
                    elif isinstance(item,self._symbolData.Namespace) and item.fqName()==nsName and lastComment is not None:
                        description = lastComment
                        lastComment = None

        nspage.write(namespaceHeader % {'namespacename': nsName,
            'modulename': self._module,
            'import': importcode,
            'description': self.formatDoxygen(description)})

        def nameKey(a): return a.name()
        classList = []
        for scope in nsList:
            classList.extend(self._findAllInstance(scope,self._sipSymbolData.SipClass))
        classList.sort(key=nameKey)

        # Class index (to other pages)
        self.writeNSClassIndex(nspage, classList)

        # Intra-page index
        nspage.write("""<table border="0" cellpadding="0" cellspacing="0">""")

        # enums
        enumList = [item for scope in nsList for item in scope
                if isinstance(item, self._sipSymbolData.Enum)]
        enumList.sort(key=nameKey)
        nspage.write(self.writeEnums(enumList))

        # Functions
        functionList = [item for scope in nsList for item in scope
                if isinstance(item, self._sipSymbolData.Function)]
        functionList.sort(key=nameKey)
        def all(x): return True
        if len(functionList)!=0:
            nspage.write(self.writeMethodIndex(functionList, all, "Functions", False))

        # Variables
        variableList = [item for scope in nsList for item in scope
                if isinstance(item, self._sipSymbolData.Variable)]
        variableList.sort(key=nameKey)
        nspage.write(self.writeVariables(variableList))

        nspage.write("</table>\n")

        # Build the comment map.
        commentMap ={}
        scopes = self._symbolData.lookupNamespace(nsName) if nsName!='global' else cppScopes
        for cppNS in scopes:
            lastComment = None
            for item in cppNS:
                if isinstance(item,self._symbolData.Comment):
                    lastComment = item.value()
                elif (isinstance(item,self._symbolData.Function) or isinstance(item,self._symbolData.Variable)
                        or isinstance(item,self._symbolData.Enum)) and lastComment is not None:
                    commentMap[self.commentMapKey(item)] = lastComment
                    lastComment = None

        # enum detail
        self.writeEnumDetail(nspage, enumList, commentMap)

        # Functions.
        self.writeMethodDetails(nspage, functionList, commentMap, "Function Documentation", True)

        # variables
        self.writeVariableDetails(nspage, variableList, commentMap)

        # footer
        nspage.write (htmlFooter % {'path': '../'})
        nspage.close ()

    @accepts(file,list)
    def writeNSNamespacesIndex(self, page, namespaces):
        if not namespaces:
            return

        page.write("<h2>Namespaces</h2>\n")

        def format(obj):
            indexstring = obj
            if indexstring[0].upper()=='K':
                indexstring = indexstring[1:]
            name = obj
            if name=='global':
                name = '<i>' + name + '</i>'
            cellcontents = '<a class="el" href="%s.html">%s</a>&nbsp;&nbsp;&nbsp;' % (obj,name)
            return (indexstring,cellcontents)
            
        page.write(FormatTable(namespaces, format, kmp))
        
    @accepts(file,list)
    def writeNSClassIndex(self, page, rawClassList):
        if not rawClassList:
            return

        page.write ("<h2>Class Index</h2>\n")

        def format(obj):
            if not obj.ignore():
                classname = indexstring = obj.name()
                if indexstring[0].upper()=='K':
                    indexstring = indexstring[1:]
                parentScope = obj.parentScope()
                scope = parentScope.fqName()
                if not scope:
                    cellcontents = '<a class="el" href="%s.html">%s</a>&nbsp;&nbsp;&nbsp;' \
                                    % (classname,classname)
                else:
                    cellcontents = '<a class="el" href="%s.%s.html">%s</a>&nbsp;(<a class="el" href="%s.html">%s</a>)&nbsp;&nbsp;&nbsp;' \
                                    % (scope,classname,classname,scope,scope)

                return (indexstring,cellcontents)
            else:
                return None
        
        def kmp_obj(a,b):
            return kmp(a.name(),b.name())
        page.write(FormatTable(rawClassList, format, kmp_obj))

    @staticmethod
    def WriteAllClasses(htmldst, nsNames, classNames):

#        self.mainIndex = open(os.path.join(htmldst, 'index.txt'), 'r')
#        for line in self.mainIndex:
#            specifier, name = line.split (':')
#            name = name.strip ()
#            if specifier == 'm':
#                module = name
#            elif specifier == 'n':
#                if name in ['global', 'Sonnet']:
#                    nsNames.append ((module, name, '%s - %s' % (name, module)))
#                else:
#                    nsNames.append ((module, name, name))
#            elif specifier == 'c':
#                classNames.append ((module, name, name))

        def key(x): return x[1]
        nsNames.sort(key=key)
        classNames.sort(key=key)

        page = open(os.path.join(htmldst, 'allclasses.html'), 'w')
        page.write(htmlHeader % {'title': 'PyKDE Namespace and Class Index', 'path': ''})

        # Namespaces
        page.write("<p>\n<h2>All Namespaces</h2>\n")

        def extract_name(x):
            nameparts = x.split('.')
            indexstring = nameparts[-1].lower()
            if indexstring.startswith('k'):
                indexstring = indexstring[1:]
            return indexstring

        def format(t):
            nameparts = t[1].split('.')
            indexstring = nameparts[-1].lower()
            if indexstring.startswith('k'):
                indexstring = indexstring[1:]

            name = nameparts[-1] + '&nbsp;(' + ('.'.join( [t[0]] + nameparts[:-1] )) + ')'

            cellcontents = '<a href="' + t[0] + '/' + t[1] + '.html">' + name + '</a>'
            return (indexstring,cellcontents)
        def t_cmp(a,b):
            return kmp(extract_name(a[1]), extract_name(b[1]))
        page.write(FormatTable(nsNames, format, t_cmp, columns=2))

        # Classes
        page.write("<p>\n<h2>All Classes</h2>\n")
        page.write(FormatTable(classNames, format, t_cmp, columns=2))

        page.write(htmlFooter % {'path': ''})
        page.close()

    @staticmethod
    def WriteMainPage(htmldst):
        page = open(os.path.join(htmldst, 'modules.html'), 'w')
        page.write(htmlHeader % {'title': 'KDE 4.4 PyKDE API Reference', 'path': ''})

        page.write("""<p>
<h2>KDE 4.4 PyKDE API Reference</h2>
</p>
<p>
This is the reference to the KDE API as it appears to Python programs using PyKDE. This is just
reference material, additional information about developing KDE applications using Python and the KDE API
in general can be found on <a href="http://techbase.kde.org/">Techbase</a> and in the
<a href="http://techbase.kde.org/Development/Languages/Python">Python section</a>. The reference for
<a href="http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/classes.html">PyQt 4 is here</a>.
</p>

<p>
This documentation is automatically generated from the original C++ headers and embedded documentation.
The classes, methods, functions, namespaces etc are described as they appear to Python code and
also include addition type information about expected parameters and return types. Note that
code fragments in the documentation have not been translated from C++ to Python.
</p>
""")

        page.write(htmlFooter % {'path': ''})

        page.close()

    @accepts(sipsymboldata.SymbolData.Argument,sipsymboldata.SymbolData.Entity)
    @returns(str)
    def formatArgument(self, arg, context):
        #print("argument: " + arg.argumentType())
        return self.formatType(arg.argumentType(),context)

    # formatType()
    # rObj - string, type name, may contain C++ '&' and '*' characters.
    @accepts(str,sipsymboldata.SymbolData.Entity)
    @returns(str)
    def formatType(self, ret, context):
        r = ''
        if not ret or ret == 'void':
            return ''
            
        for i in range(len(ret)):
            if not ret[i] in ('*', '&'):
                r += ret[i]

        if ret=="char":
            ret = "QString"
        
        #if rObj.parentScope():
        #    r = '.'.join ([rObj.parentScope().fqName(), r])
        r = self.linkType(r, context)
        return r

    CppPythonTypeMapping = {
        'bool': 'bool',
        'int': 'int',
        'float': 'float',
        'long': 'long',
        'qint32': 'int',
        'quint16': 'int',
        'qint64': 'long',
        'quint32': 'long',
        'uint': 'long',
        'qlonglong': 'long',
        'qulonglong': 'long',
        'double': 'float',
        'unsigned int': 'long',
        'unsigned long': 'long',
        'qreal': 'float',
        'unsigned short': 'long'
    }
        
    def linkType(self, typeName,context):
        if typeName.startswith("const "):
            typeName = typeName[6:]
        while typeName.endswith('*') or typeName.endswith('&'):
            typeName = typeName[:-1]

        if typeName == '...':
            return typeName

        if typeName == 'char':
            typeName = 'QString'

        # Handle QList<...>
        if typeName.startswith("QList<"):
            return '[' + self.linkType(typeName[6:-1],context) + ']'

        if typeName.startswith("QHash<"):
            pivot = typeName.index(",")
            leftType = self.linkType(typeName[6:pivot],context)
            rightType = self.linkType(typeName[pivot+1:-1],context)
            return '{' + leftType + ':'+ rightType + '}'

        if typeName.startswith("Qt.") or typeName.startswith("Qt::"):
            return '<a href="http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qt.html">' + typeName + '</a>'
        
        pyType = self.CppPythonTypeMapping.get(typeName)
        if pyType is not None:
            return pyType
        
        fileName = typeName.replace('::','.')
        try:
            typeObject = self._sipSymbolData.lookupType(typeName,context)
            #print("typeObject: "+repr(typeObject))
            #print("typeObject.topScope():"+repr(typeObject.topScope()))
            typeModule = typeObject.topScope().module()
            #print("typeObject.topScope().module(): " + repr(typeModule))
            if typeModule.startswith("PyQt"):
                return '<a href="http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/' + typeName.lower() + '.html">' + typeObject.fqPythonName() + '</a>'
            elif typeModule.startswith("PyKDE4"):
                if isinstance(typeObject,self._sipSymbolData.Enum):
                    parentScope = typeObject.parentScope()
                    if isinstance(parentScope,self._sipSymbolData.TopLevelScope):
                        parentPythonName = "global"
                    else:
                        parentPythonName = parentScope.fqPythonName()
                    fileName = parentPythonName + ".html#" + linkId(typeObject)
                else:
                    fileName = typeObject.fqPythonName() + ".html"
                return '<a href="../' + typeModule[7:] + '/' + fileName + '">' + typeObject.fqPythonName() + '</a>'
        except KeyError:
            print("KeyError: Couldn't resolve '"+typeName+"'")

        return typeName
        
    @accepts(str)
    @returns(str)
    def stripComment(self, text):
        parts = text.split('\n')
        parts[0] = parts[0].strip()
        if parts[0]=='/**':
            parts[0] = None
        parts[-1] = parts[-1].strip()
        if parts[-1]=='**/' or parts[-1]=='*/':
            parts[-1] = None
        
        # Transform for each line
        def clean(line):
            line = line.strip()
            if line.startswith('*'):
                return line[1:]
            else:
                return line
        return '\n'.join( (clean(line) for line in parts if line is not None) )

    @accepts(str)
    @returns(str)
    def formatDoxygen(self, text):
        if text:
            return reducer.do_txt(self.stripComment(text))
        else:
            return ''

def AnnotationRule(methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations):
    return cpptosiptransformer.MethodAnnotationRule(methodTypeMatch,parameterTypeMatch,parameterNameMatch,annotations)

def PySlotRule(className=None,namespaceName=None,arg1Name=None,arg2Name=None):
    return cpptosiptransformer.PySlotRule(className,namespaceName,arg1Name,arg2Name)


def pyName(obj):
    for anno in obj.annotations():
        if anno.startswith("PyName"):
            return anno[7:]
    return obj.name()

def linkId(obj):
    if obj.name() is not None:
        return obj.name()
    else:
        return 'obj'+str(id(obj))

def isSipClassAbstract(sipClass):
    for anno in sipClass.annotations():
        if anno=="Abstract":
            return True
    return False

def BuildSubclassMap(scopeList,symbolData):
    mapping = {}
    def processScope(scope):
        for item in scope:
            if isinstance(item,symbolData.SipClass):
                class_ = item
                for baseName in class_.bases():
                    try:
                        base = symbolData.lookupType(baseName,class_.parentScope())
                        if isinstance(base, symbolData.Typedef):
                            print("Warning: %s Skipping typedef base '%s'." % (class_.sourceLocation(),baseName))
                            continue

                        subClassList = mapping.setdefault(base,set())
                        subClassList.add(class_)
                    except KeyError:
                        print("Warning: %s Unrecognized type '%s'." % (class_.sourceLocation(),baseName))
            elif isinstance(item,symbolData.Namespace):
                processScope(item)

    for scope in scopeList:
        processScope(scope)
    return mapping
    
def FetchDocs(filename):
    lex = cpplexer.CppLexer()
    
    with open(filename) as fhandle:
        data = fhandle.read()
        
    lex.input(data)
    while True:
        tok = lex.token()
        if not tok:
            break      # No more input
        if tok.type=='DOC':
            print(tok)
            return tok.value
    return ""
    
def kmp(a,b):
    if a.startswith('K'):
        a = a[1:]
    if b.startswith('K'):
        b = b[1:]
    return cmp(a.lower(),b.lower())

# (indexstring,cellcontents) = cellFunc(obj)
def FormatTable(rawObjectList, cellFunc, cmpFunc=cmp, columns=3):
    if not rawObjectList:
        return

    # Sort the class list with special treatment for the letter K.
    objectList = rawObjectList[:]
    objectList.sort(cmpFunc)

    result = []

    cells = []
    letter = None
    for obj in objectList:
        tup = cellFunc(obj)
        if tup is None:
            continue
        indexstring, cellcontents = tup

        newletter = indexstring[0].upper()
        if newletter!=letter:
            letter = newletter
            cells.append('<a name="letter_'+letter+'">&nbsp;&nbsp;'+letter+'&nbsp;&nbsp;</a>')
        cells.append(cellcontents)

    # Write it out.
    result.append("""<table width="95%" align="center" border="0" cellpadding="0" cellspacing="0">
<tbody>""")

    def cell(i): return cells[i] if i<len(cells) else ''

    section = int((len(cells)+columns-1)/columns)
    for i in range(section):
        result.append("<tr>")
        for j in range(columns):
            result.append("<td>" + cell(j*section + i) + "</td>")
        result.append("</tr>\n")
    result.append("</table>\n")

    return "".join(result)


# name
htmlHeader = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">

<head>
  <title>%(title)s</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <meta http-equiv="Content-Style-Type" content="text/css" />
  <link rel="stylesheet" type="text/css" href="%(path)scommon/doxygen.css" />
  <link rel="stylesheet" media="screen" type="text/css" title="KDE Colors" href="%(path)scommon/kde.css" />
</head>
<body>
<div id="container">
<div id="header">
  <div id="header_top">
    <div>
      <div>
        <img alt ="" src="%(path)scommon/top-kde.jpg"/>
        KDE 4.4 PyKDE API Reference
      </div>
    </div>
  </div>
  <div id="header_bottom">
    <div id="location">
      <ul>
        <li>KDE's Python API</li>
      </ul>
    </div>

    <div id="menu">
      <ul>
        <li><a href="%(path)smodules.html">Overview</a></li>
<li><a href="http://techbase.kde.org/Development/Languages/Python">PyKDE Home</a></li>
<li><a href="http://kde.org/family/">Sitemap</a></li>
<li><a href="http://kde.org/contact/">Contact Us</a></li>
</ul>
    </div>
  </div>
</div>

<div id="body_wrapper">
<div id="body">
<div id="right">
<div class="content">
<div id="main">
<div class="clearer">&nbsp;</div>
"""
# nothing
htmlFooter = """
</div>
</div>
</div>

<div id="left">

<div class="menu_box">
<div class="nav_list">
<ul>
<li><a href="%(path)sallclasses.html">Full Index</a></li>
</ul>
</div>

<a name="cp-menu" /><div class="menutitle"><div>
  <h2 id="cp-menu-project">Modules</h2>
</div></div>
<div class="nav_list">
<ul>""" + (
"""<li><a href="%(path)sakonadi/index.html">akonadi</a></li>
<li><a href="%(path)sdnssd/index.html">dnssd</a></li>
<li><a href="%(path)skdecore/index.html">kdecore</a></li>
<li><a href="%(path)skdeui/index.html">kdeui</a></li>
<li><a href="%(path)skhtml/index.html">khtml</a></li>
<li><a href="%(path)skio/index.html">kio</a></li>
<li><a href="%(path)sknewstuff/index.html">knewstuff</a></li>
<li><a href="%(path)skparts/index.html">kparts</a></li>
<li><a href="%(path)skutils/index.html">kutils</a></li>
<li><a href="%(path)snepomuk/index.html">nepomuk</a></li>
<li><a href="%(path)sphonon/index.html">phonon</a></li>
<li><a href="%(path)splasma/index.html">plasma</a></li>
<li><a href="%(path)spolkitqt/index.html">polkitqt</a></li>
<li><a href="%(path)ssolid/index.html">solid</a></li>
<li><a href="%(path)ssoprano/index.html">soprano</a></li>""" if False else
"""<li><a href="%(path)smarble/index.html">marble</a></li>""") + \
"""
</ul></div></div>

</div>

</div>
  <div class="clearer"/>
</div>

<div id="end_body"></div>
</div>
<div id="footer"><div id="footer_text">
This documentation is maintained by <a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;simon&#64;simonzone&#46;com">Simon Edwards</a>.<br />
        KDE<sup>&#174;</sup> and <a href="../images/kde_gear_black.png">the K Desktop Environment<sup>&#174;</sup> logo</a> are registered trademarks of <a href="http://ev.kde.org/" title="Homepage of the KDE non-profit Organization">KDE e.V.</a> |
        <a href="http://www.kde.org/contact/impressum.php">Legal</a>
    </div></div>
</body>
</html>
"""

#nsName, module, nsName, text
namespaceHeader = """
<h1>%(namespacename)s Namespace Reference</h1>
<code>%(import)s</code>
<p>
<h2>Detailed Description</h2>
%(description)s
"""

classListEntry = '<a href="%s.html">%s</a>'
igclassListEntry = '<i style="color : #999999">%s</i>'

# classname, abstract, modulename, namespace, classname, baseclasses, description
classHeader = """
<h1>%(classname)s Class Reference</h1>
<code>from %(modulename)s import *</code>
<p>
%(baseclasses)s
%(subclasses)s
%(namespace)s
<h2>Detailed Description</h2>
%(abstract)s
%(description)s
"""

varEntry   = '<tr><td width="60%%" valign="top"><b>%s</b> <i>%s</i></td><td width="40%%" align="left">%s</td></tr>\n'
