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

import sys
import re
import ply.yacc as yacc
import cpplexer
import pplexer

class CppParser(object):
    def __init__(self):
        self.lexer = cpplexer.CppLexer()
        self.lexer.begin('variable')
        self._resetState()
        self.tokens = cpplexer.tokens
        yacc.yacc(module = self, tabmodule = "cppParserTab")
        self._parse = yacc.parse
        self._preprocessValue = {}
        self._preprocessSubstitutionMacros = []

    def _resetState(self):
        self.filename = None
        self._scopeStack = []
        self.scope = None
        self.access = "private"
        self.currentFunction = None
        self.currentEnum = None
        self.currentClass = None
        self.inTypedef = False

        self.arguments      = []
        self.templateParams = []
        self.storage        = ''
        self.inline         = False
        self.template       = None
        self.exprElements   = []
        
    def setBareMacros(self,macroList):
        self.lexer.lexmodule.setBareMacros(macroList)

    def setMacros(self,macroList):
        self.lexer.lexmodule.setMacros(macroList)
        
    def setPreprocessValues(self,valueList):
        self._preprocessValue = valueList
        
    def setPreprocessSubstitutionMacros(self,macroList):
        self._preprocessSubstitutionMacros = macroList
        
    def parse(self, symbolData, text, filename=None, debugLevel = 0):
        self._resetState()

        self.symbolData = symbolData
        self.scope = self.symbolData.topScope()
        
        chewedText = pplexer.preprocess(text, self._preprocessValue, self.__compileMacros(self._preprocessSubstitutionMacros))

        self.lexer.input(chewedText)
        self.lexer.lineno = 1
        self.lexer.lexpos = 0 

        result = self._parse(debug = debugLevel, lexer = self.lexer)
        return result
        
    def __compileMacros(self, macroList):
        # Convert the list of macros to regular expressions. Macro which are
        # already regexs don't need to changed. Bare string macros and their
        # substituation strings are treated as straight string substituations.
        compiledMacros = []
        for item in macroList:
            if not isinstance(item[0],str):
                compiledMacros.append(item)
            else:
                compiledMacros.append( (re.compile(item[0]), re.escape(item[1])) )
        return compiledMacros

    def _pushScope(self, newScope):
        self._scopeStack.append(self.scope)
        self.scope = newScope

    def _popScope(self):
        self.scope = self._scopeStack.pop()

    def object_id_list (self, id_list, obj, objType = None):
        idList = id_list.split (',')
        if self.inTypedef:
            self.stateInfo.currentObject ().name = idList [0]
            for id in idList [1:]:
                originalObj = self.stateInfo.popObject ()                
                if obj == 'class':
                    newObj = self.classObject (id, objType)
                elif obj == 'enum':
                    newObj = self.enumObject (id)
                    newObj.enumerators = originalObj.enumerators
        else:
            for id in idList:
                self.variableObject (id, self.stateInfo.currentObject ().name)         
    
    def classObject (self, name, type_):
        class_ = self.symbolData.CppClass(self.scope, name, self.filename, self.lexer.lineno)
        self.currentClass = class_
        self._pushScope(class_)

        if type_ == 'class':
            class_.setAccess('private')
        else:
            class_.setAccess('public')
    
    def enumObject (self, name):
        enum = self.symbolData.Enum(self.scope, name, self.filename, self.lexer.lineno)
        enum.setAccess(self.access)
        self.currentEnum = enum
        return enum
    
    def typedefObject(self, typeName, newName):
        tdObj = self.symbolData.Typedef(self.scope, newName, self.filename, self.lexer.lineno)
        tdObj.setArgumentType(typeName)
#        if typeName.startswith('QFlags<'):
#            tdObj.template = Template('QFlags', typeName [7:-1])
#       else:
#            tdObj.template = self.template
#        self.template = None
        self._pushScope(tdObj)
        self.currentTypedef = tdObj
            
        return tdObj
        
    def bareMacro(self,name):
        macro = self.symbolData.ScopedMacro(self.scope, name, self.filename, self.lexer.lineno)
        return macro
    
    def argument(self, argumentType, argumentName = None, argumentValue = None):
        self.arguments.append ((argumentType, argumentName, argumentValue, self.template, self.exprElements))
        self.template = None
        self.exprElements = []
        return self.arguments
    
    def argumentList(self):
        instanceList = []
        for argTuple in self.arguments:
            vtype, name, init, template, exprElements = argTuple
            instanceList.append(self.symbolData.Argument(vtype, name, init, template))
        return instanceList

    def variableObject(self, name, vtype, init = None):
        vObj = self.symbolData.Variable(self.scope, name, self.filename, self.lexer.lineno)
        vObj.setArgument(self.symbolData.Argument(vtype, name, init, None, self.template))
        vObj.setStorage(self.storage)
        vObj.setAccess(self.access)
        
        self.storage = None
        self.template = None
        return vObj
        
    def functionObject(self, name, returns):
        if returns=='ctor':
            functionObj = self.symbolData.Constructor(self.scope, name, self.filename, self.lexer.lineno)
        elif returns=='dtor':
            functionObj = self.symbolData.Destructor(self.scope, name, self.filename, self.lexer.lineno)
        else:
            functionObj = self.symbolData.Function(self.scope, name, self.filename, self.lexer.lineno)
            returnArg = self.symbolData.Argument(returns)
            functionObj.setReturn(returnArg)

        #self.template = None
        self.exprElements = []

        functionObj.setStorage(self.storage)
        self.storage = None

        #functionObj.templateParams = self.stateInfo.inTemplate
        #self.stateInfo.inTemplate = []
        
        self.currentFunction = functionObj
        
        if self.lexer.lexstate not in ['stmt', 'operator']:
            self.lexer.begin ('function')
        return functionObj
                        
    precedence = (('right','UMINUS'), )
    #precedence = (('left','+','-'), ('left','*','/'), ('right','UMINUS'), )
    
    # start
    def p_declarations (self, p):
        """declarations : member
                        | member_list member"""
        pass
        
    def p_member (self, p):
        """member : namespace_decl
                  | class_decl
                  | enum_decl
                  | typedef_decl
                  | q_declare_flags
                  | function_decl
                  | variable_decl
                  | template_decl
                  | bare_macro
                  | skip_macro"""
        pass
        #self.lexer.begin (self.stateInfo.lexState)
        #self.stateInfo.lexState  = 'variable'
        #self.stateInfo.inTypedef = False
        #self.arguments    = []
        #self.template     = None
        #self.exprElements = []
                  
    def p_member_list (self, p):
        """member_list : member
                       | member_list member"""
        pass

    def p_namespace_decl0 (self, p):
        'namespace_decl : namespace_name LBRACE member_list RBRACE'
        self._popScope()
        
    def p_namespace_decl1 (self, p):
        'namespace_decl : namespace_name LBRACE RBRACE'
        self._popScope()        
        
    def p_namespace_decl2 (self, p):
        'namespace_decl : namespace LBRACE member_list RBRACE'
        pass
        
    def p_namespace_name (self, p):
        'namespace_name : namespace ID'
        name = p[2]
        namespace = self.symbolData.Namespace(self.scope, name, self.filename, self.lexer.lineno)
        self._pushScope(namespace)
                        
    def p_empty (self, p):
        'empty :'
        pass
 
    def p_decl_end (self, p):
        """decl_end : SEMI
                   | inline_code"""
        pass
        
    def p_class_decl0 (self, p):
        """class_decl : class_header class_member_list RBRACE decl_end
                      | opaque_class
                      | class_header RBRACE decl_end"""
        #name, obj = self.stateInfo.popClass ()
        self._popScope()
        #if not obj.opaque:
        #    self.symbolData.objectList.append (EndClassMarker (name, self.lexer.lineno, self.stateInfo))
    
    def p_class_decl1 (self, p):
        'class_decl : class_header class_member_list RBRACE id_list decl_end'
        if p [1] in ['class', 'struct', 'union']:
            self.object_id_list (p [4], p [1])
        else:
            self.object_id_list (p [4], 'class')
        name, obj = self.stateInfo.popClass ()
        
    def p_class_member (self, p):
        """class_member : class_decl
                        | enum_decl
                        | typedef_decl
                        | q_declare_flags
                        | access_specifier
                        | function_decl
                        | variable_decl
                        | template_decl
                        | bare_macro
                        | skip_macro"""
        #if self.stateInfo.lexState != 'operator':
        #   self.lexer.begin (self.stateInfo.lexState)
        #self.stateInfo.lexState  = 'variable'
        #self.stateInfo.inTypedef = False

        self.arguments   = []
        self.template    = None
        self.exprElement = None
            
    def p_access_specifier (self, p):
        """access_specifier : public COLON
                            | public slots COLON
                            | protected COLON
                            | protected slots COLON
                            | private COLON
                            | private slots COLON
                            | signals COLON
                            | slots COLON"""
        self.access = p[1]

    def p_base_access_specifier (self, p):
        """base_access_specifier : public
                                 | protected
                                 | private"""
        pass

    def p_class_member_list (self, p):
        """class_member_list : class_member
                             | class_member_list class_member"""
        pass

    
    def p_class_header0 (self, p):
        """class_header : class_name LBRACE
                        | class_name COLON base_list LBRACE
                        | class_from_typedef"""
        p [0] = p [1]
        
    def p_class_header1 (self, p):
        """class_header : union LBRACE
                        | struct LBRACE"""
        self.classObject('anonymous', p[1])
    
    def p_class_name (self, p):
        """class_name : class ID
                      | struct ID
                      | union ID
                      | class template_type"""
        self.classObject(p[2], p[1])
        
    def p_class_name1 (self, p):
        """class_name : class BAREMACRO ID
                      | struct BAREMACRO ID
                      | union BAREMACRO ID
                      | class BAREMACRO template_type"""
        self.classObject(p[3], p[1])
        self.currentClass.addMacro(self.symbolData.Macro(p[2]))
        
    def p_opaque_class (self, p):
        'opaque_class : class_name SEMI'
        self.currentClass.setOpaque(True)
    
    def p_base_list_element0 (self, p):
        """base_list_element : base_access_specifier qualified_id
                            | base_access_specifier template_type"""
        self.currentClass.addBase(p[2])

    def p_base_list_element1 (self, p):
        """base_list_element : virtual base_access_specifier qualified_id
                            | virtual base_access_specifier template_type"""
        self.currentClass.addBase(p[3])
     
    def p_base_list_element2 (self, p):
        'base_list_element : qualified_id'
        self.currentClass.addBase(p[1])

    def p_base_list (self, p):
        """base_list : base_list_element
                     | base_list COMMA base_list_element"""
        pass

    def p_enum_decl0 (self, p):
        'enum_decl : enum_statement SEMI'
        self.currentEnum = None
        
    def p_enum_decl1 (self, p):
        'enum_decl : enum_statement id_list SEMI'
        self.object_id_list (p [2], 'enum')
        self.currentEnum = None
        
    def p_enum_statement (self, p):
        """enum_statement : enum_name enumerator_list RBRACE
                                       | enum_name RBRACE"""
        self.lexer.begin ('variable')
        
    def p_enum_name0 (self, p):
        """enum_name : enum ID LBRACE
                     | enum LBRACE"""                     
            
        if p[2] != "{":
            name = p[2]
        else:
            name = None
        self.enumObject(name)
        
    def p_enum_name1 (self, p):
        'enum_name : enum_from_typedef'
        self._popScope()
        self.currentTypedef = None
        
    def p_enumerator0 (self, p):
        """enumerator : ID
                      | ID EQUALS expression"""
                
        if len(p) == 4:
            enumerator = self.symbolData.Enumerator(p[1], p[3])
        else:
            enumerator = self.symbolData.Enumerator(p[1], None)
        self.currentEnum.appendEnumerator(enumerator)
    
    def p_enumerator1 (self, p):
        """enumerator : DOC ID
                      | DOC ID EQUALS expression"""
                
        if len (p) == 5:
            enumerator = self.symbolData.Enumerator(p[2], p[4])
        else:
            enumerator = self.symbolData.Enumerator(p[2], None)
        enumerator.setDoc(p[1])
        self.currentEnum.appendEnumerator(enumerator)
        
    def p_enumerator2 (self, p):
        """enumerator : ID UPDOC
                      | ID EQUALS expression UPDOC"""
        
        if len (p) == 5:
            enumerator = self.symbolData.Enumerator(p[1], p[3], self.stateInfo)
            enumerator.setDoc(p[4])
        else:
            enumerator = self.symbolData.Enumerator(p[1], None, self.stateInfo)
            enumerator.setDoc(p[2])
        self.currentEnum.appendEnumerator(enumerator)

    def p_enumerator_list0 (self, p):
        """enumerator_list : enumerator
                           | enumerator_list enum_delim enumerator
                           | enumerator_list UPDOC"""
        if len (p) == 3:
            self.currentObject ().enumerators [-1].doc = p [2]
        
    def p_enum_delim0 (self, p):
        """enum_delim : COMMA
                      | COMMA UPDOC"""
        if len (p) == 3:
            self.stateInfo.currentObject ().enumerators [-1].doc = p [2]
        
    def p_enum_delim1 (self, p):
        'enum_delim : COMMA UPDOC DOC'
        self.stateInfo.currentObject ().enumerators [-1].doc = p [2]

    def p_enum_delim2 (self, p):
        """enum_delim : COMMA DOC
                      | DOC COMMA"""
        pass

    def p_id_list_element0 (self, p):
        'id_list_element : ID'
        p [0] = p [1]
        
    def p_id_list_element1 (self, p):
        """id_list_element : ASTERISK ID
                                    | AMPERSAND ID"""
        p [0] = "".join (p [1:])

    def p_id_list (self, p):
        """id_list : id_list_element
                   | id_list COMMA id_list_element"""
        p [0] = "".join (p [1:])
                   
    def p_qualified_id (self, p):
        """qualified_id : ID
                        | nested_name_specifier"""
        p [0] = p [1]
                        
    def p_nested_name_specifier0 (self, p):
        """nested_name_specifier : ID COLON2 ID
                                 | nested_name_specifier COLON2 ID
                                 | template_type COLON2 ID"""                                 
        p [0] = "".join (p [1:])

    def p_nested_name_specifier1 (self, p):
        'nested_name_specifier : COLON2 ID'
        p [0] = p [2]
        
    def p_template_type (self, p):
        """template_type : qualified_id LT type_specifier_list GT
                        | qualified_id LT static_cast_expression GT"""
        
        p[0] = "".join (p[1:])
        #self.template = Template(p[1], p[3], self.template)
        
    def p_elaborated_type (self, p):
        """elaborated_type : enum qualified_id
                           | class qualified_id
                           | struct qualified_id
                           | union qualified_id
                           | typename qualified_id"""
        p [0] = p [2]
                   
    def p_type_specifier_base (self, p):
        """type_specifier_base : qualified_id
                               | template_type
                               | elaborated_type
                               | int
                               | unsigned int
                               | signed int
                               | char
                               | unsigned char
                               | signed char
                               | float
                               | double
                               | long
                               | long int
                               | unsigned long
                               | unsigned long int
                               | long unsigned int
                               | signed long
                               | signed long int
                               | long long
                               | unsigned long long
                               | signed long long
                               | signed long long int
                               | short
                               | unsigned short
                               | signed short
                               | short int
                               | unsigned short int
                               | signed short int
                               | unsigned
                               | signed
                               | bool
                               | void
                               | wchar_t"""
        p [0] = " ".join (p [1:])
        
    def p_type_specifier0 (self, p):
        'type_specifier : type_specifier_base '
        p [0] = p [1]

    def p_type_specifier1 (self, p):
        'type_specifier : CVQUAL type_specifier_base'
        p [0] = '%s %s' % (p [1], p[2])
                          
    def p_type_specifier2 (self, p):
        'type_specifier : type_specifier_base type_decorator'
        p [0] = '%s%s' % (p [1], p[2])
        
    def p_type_specifier3 (self, p):
        'type_specifier : CVQUAL type_specifier_base type_decorator'
        p [0] = '%s %s%s' % (p [1], p[2], p[3])

    def p_type_specifier4 (self, p):
        'type_specifier : type_specifier_base CVQUAL type_decorator'
        p [0] = '%s %s%s' % (p [2], p[1], p[3])

    def p_type_decorator (self, p):
        """type_decorator : ASTERISK
                          | AMPERSAND
                          | ASTERISK CVQUAL
                          | ASTERISK AMPERSAND
                          | ASTERISK ASTERISK
                          | ASTERISK ASTERISK ASTERISK
                          | ARRAYOP"""
        p [0] = "".join (p [1:])
        
    def p_type_specifier_list (self, p):
        """type_specifier_list : type_specifier
                               | type_specifier_list COMMA type_specifier"""
        p [0] = "".join (p [1:])
                   
    def p_typedef_decl (self, p):
        """typedef_decl : typedef_simple SEMI
                        | typedef_elaborated SEMI
                        | typedef_function_ptr SEMI"""
        self._popScope()
        self.currentTypedef = None
       
    def p_typedef_simple0 (self, p):
        'typedef_simple : typedef type_specifier ID'
        self.typedefObject(p[2], p[3])
        self.inTypedef = True
        
    def p_typedef_simple1 (self, p):
        'typedef_simple : typedef type_specifier ID ARRAYOP'
        self.typedefObject('%s*' % p [2], p [3])
        self.inTypedef = True

    def p_q_declare_flags_name (self, p):
        'q_declare_flags_name : Q_DECLARE_FLAGS LPAREN ID COMMA ID'
        self.typedefObject("QFlags<%s>" % p [5], p [3]);
        
    def p_q_declare_flags (self, p):
        'q_declare_flags : q_declare_flags_name RPAREN'
        self.stateInfo.popObject ()
        
    def p_typedef_elaborated (self, p):
        """typedef_elaborated : typedef class qualified_id ID
                              | typedef struct qualified_id ID
                              | typedef union qualified_id ID
                              | typedef enum qualified_id ID"""
        self.typedefObject(p[3], p[4])
        self.inTypedef = True
        
    def p_class_from_typedef0 (self, p):
        """class_from_typedef : typedef class ID LBRACE
                              | typedef struct ID LBRACE
                              | typedef union ID LBRACE"""
        p [0] = p [2]
        self.classObject (p [3], p [2])
        self.inTypedef = True
        
    def p_class_from_typedef1 (self, p):
        """class_from_typedef : typedef struct LBRACE
                              | typedef union LBRACE"""
        p [0] = p [2]
        self.classObject ('anonymous', p [2])
        self.inTypedef = True

    def p_enum_from_typedef (self, p):
        """enum_from_typedef : typedef enum ID LBRACE
                             | typedef enum LBRACE"""
        if p [3] != "{":
            name = p [3]
        else:
            name = None
            
        tdObj = self.symbolData.Typedef(self.scope, name, self.filename, self.lexer.lineno)
        self.template = None
        self._pushScope(tdObj)
        self.currentTypedef = tdObj

        self.inTypedef = True
        self.enumObject(name)
        
    def p_pointer_to_function_pfx (self, p):
        """pointer_to_function_pfx : ASTERISK FUNCPTR
                                   | type_specifier FUNCPTR"""
        if p[1] == '*':
            p [0] = '*%s' % p[2]
        else:
            p [0] = " ".join (p[1:])
        
    def p_pointer_to_function_name (self, p):
        'pointer_to_function_name : pointer_to_function_pfx ID'
        p [0] = "|".join ([p[1], p[2]])
        
    def p_pointer_to_function_args (self, p):
        """pointer_to_function_args : RPAREN LPAREN type_specifier_list
                                    | RPAREN LPAREN empty"""
        p [0] = p [3]
        
    def p_pointer_to_function (self, p):
        'pointer_to_function : pointer_to_function_name pointer_to_function_args RPAREN'
        if p [2]:
            p [0] = "|".join ([p [1], p [2]])
        else:
            p [0] = "|".join ([p [1], ""])
                
    def p_typedef_function_ptr (self, p):
        'typedef_function_ptr : typedef pointer_to_function'
        ptrType, name, args = p [2].split ('|', 2)
        typedefObj = self.typedefObject (ptrType, name)
        if args:
            typedefObj.functionPtr = args.split (',')
        else:
            typedefObj.functionPtr = ['()']
        self.inTypedef = True
        
    def p_array_variable (self, p):
        'array_variable : ID ARRAYOP'
        p [0] = " ".join (p [1:])
                
    def p_argument_specifier0 (self, p):
        """argument_specifier : type_specifier
                              | ELLIPSIS"""
        p [0] = self.argument (p [1])
        
    def p_argument_specifier1 (self, p):
        """argument_specifier : type_specifier ID
                              | type_specifier array_variable"""
        p [0] = self.argument (p [1], p [2])

    def p_argument_specifier2 (self, p):
        'argument_specifier : type_specifier EQUALS expression'
        p [0] = self.argument (p [1], None, p [3])
        
    def p_argument_specifier3 (self, p):
        """argument_specifier : type_specifier ID EQUALS expression
                              | type_specifier array_variable EQUALS expression"""
        p [0] = self.argument (p [1], p [2], p [4])
        
    def p_argument_specifier4 (self, p):
        'argument_specifier : pointer_to_function'
        argType, name, args = p [1].split ('|', 2)
        p[0] = self.argument('$fp' + argType, name, args)
                              
    def p_argument_list0 (self, p):
        """argument_list : argument_specifier"""
#                         | type_specifier"""
        p [0] = [p [1]]
        
    def p_argument_list1 (self, p):
        """argument_list : argument_list COMMA argument_specifier
                         | argument_list COMMA type_specifier"""
        if p [0]:
            p [0].append (p [3])
        else:
            p [0] = [p [3]]

    def p_decl_starter0 (self, p):
        'decl_starter : type_specifier qualified_id'
        p [0] = "|".join (p [1:])
        
    def p_decl_starter1 (self, p):
        'decl_starter : STORAGE type_specifier qualified_id'
        p [0] = "|".join (p [2:])
        self.storage = p [1]
            
    def p_variable_decl0 (self, p):
        'variable_decl : decl_starter SEMI'
        vtype, name = p [1].split ('|')
        self.variableObject (name, vtype)
    
    def p_variable_decl1 (self, p):
        'variable_decl : argument_specifier SEMI'
        vtype, name, init = p[1][0][:3]
        self.variableObject (name, vtype, init)
        
    def p_variable_decl2 (self, p):
        'variable_decl : STORAGE argument_specifier SEMI'
        vtype, name, eqsign, init = p [2][0][:4]
        self.variableObject (name, vtype, init)
    
    def p_variable_decl3 (self, p):
        'variable_decl : type_specifier id_list SEMI'
        vtype = p [1]
        names = p[2].split (',')
        for name in names:
            self.variableObject (name, vtype)           
                
    def p_variable_decl4 (self, p):
        'variable_decl : STORAGE type_specifier id_list SEMI'
        self.storage = p[1]
        vtype = p [2]
        names = p[3].split (',')
        for name in names:
            self.variableObject (name, vtype)           

    def p_variable_decl5 (self, p):
        'variable_decl : type_specifier CVQUAL ID SEMI'
        vObj = self.variableObject (p [3], p [1])
        vObj.variable.attributes.cv = p [2]
        
    def p_variable_decl6 (self, p):
        'variable_decl : type_specifier ID COLON ICONST SEMI'
        vObj = self.variableObject (p [2], p [1])
        vObj.bitmap = p [4]

    def p_variable_decl7 (self, p):
        'variable_decl : pointer_to_function SEMI'
        varType, name, args = p [1].split ("|", 2)
        varObj = self.variableObject (name, varType, None)
        
        if args:
            varObj.functionPtr = args.split (',')
        else:
            varObj.functionPtr = []
            
    def p_function_name (self, p):
        'function_name : decl_starter LPAREN'
        returns, name = p [1].split ('|')
        func = self.functionObject(name, returns)
        func.setAccess(self.access)
        self.arguments = []
        
    def p_operator_pfx (self, p):
        'operator_pfx : type_specifier operator'
        p [0] = p [1]      
        
    def p_operator_name (self, p):
        """operator_name : operator_pfx PLUS LPAREN
                         | operator_pfx MINUS LPAREN
                         | operator_pfx ASTERISK LPAREN
                         | operator_pfx SLASH LPAREN
                         | operator_pfx PERCENT LPAREN
                         | operator_pfx VBAR LPAREN
                         | operator_pfx AMPERSAND LPAREN
                         | operator_pfx LT LPAREN
                         | operator_pfx LT LT LPAREN
                         | operator_pfx GT LPAREN
                         | operator_pfx GT GT LPAREN
                         | operator_pfx LOR LPAREN
                         | operator_pfx LAND LPAREN
                         | operator_pfx BANG LPAREN
                         | operator_pfx LE LPAREN
                         | operator_pfx GE LPAREN
                         | operator_pfx EQ LPAREN
                         | operator_pfx EQUALS LPAREN
                         | operator_pfx TIMESEQUAL LPAREN
                         | operator_pfx DIVEQUAL LPAREN
                         | operator_pfx MODEQUAL LPAREN
                         | operator_pfx PLUSEQUAL LPAREN
                         | operator_pfx MINUSEQUAL LPAREN
                         | operator_pfx LSHIFTEQUAL LPAREN
                         | operator_pfx GT GE LPAREN
                         | operator_pfx ANDEQUAL LPAREN
                         | operator_pfx OREQUAL LPAREN
                         | operator_pfx XOREQUAL LPAREN
                         | operator_pfx PLUSPLUS LPAREN
                         | operator_pfx MINUSMINUS LPAREN
                         | operator_pfx ARRAYOP LPAREN
                         | operator_pfx LPAREN RPAREN LPAREN
                         | operator_pfx ARROW LPAREN
                         | operator_pfx NE LPAREN"""
        n = len (p) - 1
        self.functionObject ('operator ' + "".join (p [2:n]), p[1])
        self.arguments = []
        
    def p_cast_operator_name0 (self, p):
        'cast_operator_name : operator type_specifier LPAREN RPAREN'
        self.functionObject ('operator ' + p [2], p[2])
        self.arguments  = []
        
    def p_cast_operator_name1 (self, p):
        'cast_operator_name : operator type_specifier LPAREN RPAREN CVQUAL'
        fObj = self.functionObject ('operator ' + p [2], p[2])
        fObj.attributes.cv = p [5]
        self.arguments  = []        
        
    def p_cast_operator_stmt (self, p):
        """cast_operator_stmt : cast_operator_name decl_end
                                        | virtual cast_operator_name decl_end"""
        self.currentFunction.setArguments(self.argumentList())
        if len(p) == 4:
            self.currentFunction.addQualifier('virtual')

    def p_operator_primary0 (self, p):
        """operator_primary : operator_name argument_list RPAREN
                            | operator_name RPAREN"""
        self.currentFunction.setArguments(self.argumentList())

    def p_operator_primary1 (self, p):
        """operator_primary : virtual operator_name argument_list RPAREN
                            | virtual operator_name RPAREN"""
        self.currentFunction.setArguments(self.argumentList())
        self.currentFunction.addQualifier('virtual')
            
    def p_operator_stmt0 (self, p):
        """operator_stmt : operator_primary decl_end
                         | operator_primary pure_virtual_suffix decl_end"""
        pass
        
    def p_operator_stmt1 (self, p):
        """operator_stmt : operator_primary CVQUAL decl_end
                         | operator_primary CVQUAL pure_virtual_suffix"""
        self.currentFunction.addQualifier(p[2])

    def p_ctor_name0 (self, p):
        'ctor_name : qualified_id LPAREN'
        self.functionObject(p[1], 'ctor')
        self.arguments = []
        
    def p_ctor_name1 (self, p):
        'ctor_name : explicit qualified_id LPAREN'
        fo = self.functionObject(p[2], 'ctor')
        fo.addQualifier('explicit')
        self.arguments = []

    def p_dtor_name (self, p):
        'dtor_name : TILDE ID'
        self.functionObject(p[2], 'dtor')
        self.arguments = []
        
    def p_virtual_dtor_name (self, p):
        'virtual_dtor_name : virtual dtor_name'
        self.arguments = []
                            
    def p_function_decl (self, p):
        """function_decl : ctor_stmt
                         | dtor_stmt
                         | function_stmt
                         | operator_stmt
                         | cast_operator_stmt
                         | virtual_stmt
                         | pure_virtual"""
        self.currentFunction = None
                                 
    def p_function_primary (self, p):
        """function_primary : function_name RPAREN
                            | function_name argument_list RPAREN"""
        self.currentFunction.setArguments(self.argumentList())
    
    def p_function_stmt0 (self, p):
        'function_stmt : function_primary decl_end'
        pass
        
    def p_function_stmt1 (self, p):
        'function_stmt : function_primary CVQUAL decl_end'
        self.currentFunction.addQualifier(p[2])
                            
    def p_ctor_primary (self, p):
        """ctor_primary : ctor_name RPAREN
                       | ctor_name argument_list RPAREN"""
        self.currentFunction.setArguments(self.argumentList())
    
    def p_ctor_initializer (self, p):
        """ctor_initializer : qualified_id LPAREN expression_list RPAREN
                            | qualified_id LPAREN RPAREN
                            | template_type LPAREN expression_list RPAREN
                            | template_type LPAREN RPAREN"""
        pass
        
    def p_ctor_initializer_list (self, p):
        """ctor_initializer_list : ctor_initializer
                                 | ctor_initializer_list COMMA ctor_initializer"""
                                 
        pass
        
    def p_ctor_stmt (self, p):
        """ctor_stmt : ctor_primary decl_end
                     | ctor_primary COLON ctor_initializer_list decl_end"""
        pass
        
    def p_dtor_primary0 (self, p):
        'dtor_primary : dtor_name LPAREN RPAREN'
        pass
        
    def p_dtor_primary1 (self, p):
        'dtor_primary : virtual_dtor_name LPAREN RPAREN'
        self.currentFunction.addQualifier('virtual')
        
    def p_dtor_stmt (self, p):
        'dtor_stmt : dtor_primary decl_end'
        pass
        
    def p_virtual_primary (self, p):
        """virtual_primary : virtual function_name RPAREN
                          | virtual function_name argument_list RPAREN"""
        self.currentFunction.setArguments(self.argumentList())
        self.currentFunction.addQualifier('virtual')
        
    def p_virtual_stmt0 (self, p):
        'virtual_stmt : virtual_primary decl_end'
        pass
    
    def p_virtual_stmt1 (self, p):
        'virtual_stmt : virtual_primary CVQUAL decl_end'
        self.stateInfo.currentObject ().attributes.cv = p [2]

    def p_pure_virtual_suffix (self, p):
        'pure_virtual_suffix : EQUALS PURESFX'
        pass
            
    def p_pure_virtual (self, p):
        """pure_virtual : virtual_primary pure_virtual_suffix 
                        | virtual_primary CVQUAL pure_virtual_suffix"""
        self.currentFunction.addQualifier('pure')
        if p[2] in ['const', 'volatile']:
            self.currentFunction.addQualifier(p[2])

    def p_template_param (self, p):
        """template_param : type_specifier
                         | type_specifier ID"""
        self.templateParams.append (" ".join (p [1:]))
        
    def p_template_param_list (self, p):
        """template_param_list : template_param
                              | template_param_list COMMA template_param"""
        pass
        
    def p_template_decl (self, p):
        'template_decl : template LT template_param_list GT'
        self.stateInfo.inTemplate = ','.join (self.templateParams)
        self.templateParams = []
                        
#     def p_skip_macro (self, p):
#         'skip_macro : MACROCALL MACROBODY'
#         pass        


# expression handling for argument default values - just parses and
# then reassembles the default value expression (no evaluation)

    def p_expression_list (self, p):
        """expression_list : expression
                          | expression_list COMMA expression"""
        pass                          

    def p_expression0 (self, p):
        """expression : add_expression
                      | sub_expression
                      | mult_expression
                      | div_expression
                      | mod_expression
                      | unary_expression
                      | or_expression
                      | and_expression
                      | xor_expression
                      | bitor_expression
                      | bitand_expression
                      | lt_expression
                      | le_expression
                      | eq_expression
                      | ge_expression
                      | gt_expression
                      | lshift_expression
                      | rshift_expression
                      | ptr_expression
                      | dot_expression
                      | new_expression
                      | static_cast_expression
                      | ICONST
                      | FCONST
                      | HEXCONST
                      | CCONST
                      | SCONST"""
        p [0] = p [1]
            
    def p_expression1 (self, p):
        'expression : LPAREN expression RPAREN'
        p [0] = "".join (p [1:])

    def p_expression2 (self, p):
        'expression : qualified_id'
        p [0] = p [1]
        self.exprElements.append (p [1])
    
    def p_expression3 (self, p):
        """expression : type_specifier LPAREN expression_list RPAREN
                      | type_specifier LPAREN RPAREN"""
        p [0] = "".join (p [1:])
        self.exprElements.append ('%s()' % p [1])
        
    def p_expression4 (self, p):
        """expression : type_specifier PERIOD ID LPAREN expression_list RPAREN
                      | type_specifier PERIOD ID LPAREN RPAREN"""
        p [0] = "".join (p [1:])
        self.exprElements.append ('%s.%s()' % (p [1], p [3]))

    def p_expression5 (self, p):
        'expression : type_specifier PERIOD ID'
        p [0] = p [1]
        self.exprElements.append ('%s.%s' % (p [1], p [3]))
    
    def p_expression_list (self, p):
        """expression_list : expression
                           | expression_list COMMA expression"""
        p [0] = "".join (p [1:])

    def p_unary_expression (self, p):
        """unary_expression : sign_expression
                            | not_expression
                            | bitnot_expression
                            | new_expression"""
        p [0] = p [1]

    def p_add_expression (self, p):
        'add_expression : expression PLUS expression'
        p [0] = "".join (p [1:])
        
    def p_sub_expression (self, p):
        'sub_expression : expression MINUS expression'
        p [0] = "".join (p [1:])
    
    def p_mult_expression (self, p):
        'mult_expression : expression ASTERISK expression'
        p [0] = "".join (p [1:])
    
    def p_div_expression (self, p):
        'div_expression : expression SLASH expression'
        p [0] = "".join (p [1:])
    
    def p_mod_expression (self, p):
        'mod_expression : expression PERCENT expression'
        p [0] = "".join (p [1:])
    
    def p_sign_expression (self, p):
        'sign_expression : MINUS expression %prec UMINUS'
        p [0] = "".join (p [1:])
    
    def p_or_expression (self, p):
        'or_expression : expression LOR expression'
        p [0] = "".join (p [1:])
    
    def p_and_expression (self, p):
        'and_expression : expression LAND expression'
        p [0] = "".join (p [1:])
    
    def p_xor_expression (self, p):
        'xor_expression : expression CARET expression'
        p [0] = "".join (p [1:])
    
    def p_bitor_expression (self, p):
        'bitor_expression : expression VBAR expression'
        p [0] = "".join (p [1:])
    
    def p_bitand_expression (self, p):
        'bitand_expression : expression AMPERSAND expression'
        p [0] = "".join (p [1:])
    
    def p_lt_expression (self, p):
        'lt_expression : expression LT expression'
        p [0] = "".join (p [1:])
    
    def p_le_expression (self, p):
        'le_expression : expression LE expression'
        p [0] = "".join (p [1:])
    
    def p_eq_expression (self, p):
        'eq_expression : expression EQ expression'
        p [0] = "".join (p [1:])
    
    def p_ge_expression (self, p):
        'ge_expression : expression GE expression'
        p [0] = "".join (p [1:])
    
    def p_gt_expression (self, p):
        'gt_expression : expression GT expression'
        p [0] = "".join (p [1:])
    
    def p_lshift_expression (self, p):
        'lshift_expression : expression GT GT expression'
        p [0] = "".join (p [1:])
    
    def p_rshift_expression (self, p):
        'rshift_expression : expression LT LT expression'
        p [0] = "".join (p [1:])

    def p_not_expression (self, p):
        'not_expression : BANG expression'
        p [0] = "".join (p [1:])

    def p_bitnot_expression (self, p):
        'bitnot_expression : TILDE expression'
        p [0] = "".join (p [1:])
    
    def p_new_expression (self, p):
        'new_expression : new expression'
        p [0] = "".join (p [1:])

    def p_static_cast_expression (self, p):
        'static_cast_expression : static_cast LT type_specifier GT LPAREN expression RPAREN'
        p [0] = ''.join (p [1:])
        self.exprElements.append (p [3])
    
    def p_ptr_expression (self, p):
        'ptr_expression : expression ARROW expression'
        p [0] = "".join (p [1:])

    def p_dot_expression (self, p):
        'dot_expression : expression PERIOD expression'
        p [0] = "".join (p [1:])

# inline code/statements
# the second and last cases are incorrect syntax, but show up in KDE
    def p_inline_code (self, p):
        """inline_code : STMT_BEGIN code_list STMT_END
                      |  STMT_BEGIN code_list STMT_END SEMI
                      | STMT_BEGIN STMT_END
                      | STMT_BEGIN STMT_END SEMI"""
        pass

    def p_code_list_block (self, p):
        """code_list_block : CODE_STMT_BEGIN code_list STMT_END
                                    | CODE_STMT_BEGIN STMT_END"""
        pass
                          
    def p_code_list (self, p):
        """code_list : CODE_TOKEN
                    | code_list_block
                    | code_list code_list_block
                    | code_list CODE_TOKEN"""

# calls to mostly ignored macros
    def p_skip_macro (self, p):
        'skip_macro : MACROCALL MACRO_CALL_BEGIN macro_call_element_list MACRO_CALL_END'
        #if p [1] == 'Q_DISABLE_COPY':
        #    fcn  = self.functionObject (p [3], 'ctor')
        #    fcn.setArguments (self.argument ('const %s&' % p[3]))
        #    self.stateInfo.popObject ()
        #else:
        #    pass
        macro = self.bareMacro(p[1])
        macro.setArgument(p[3])
        macro.setAccess(self.access)
        
    def p_bare_macro(self,p):
        'bare_macro : BAREMACRO'
        macro = self.bareMacro(p[1])
        macro.setAccess(self.access)
    
    def p_macro_call_parens (self, p):
        """macro_call_parens : LPAREN RPAREN
                            | LPAREN macro_call_element_list RPAREN"""
        pass
                            
    def p_macro_call_element_list0 (self, p):
        'macro_call_element_list : MACRO_ELEMENT'
        p [0] = p[1]

    def p_macro_call_element_list1 (self, p):
        'macro_call_element_list : macro_call_element_list MACRO_ELEMENT'
        p [0] = ' '.join (p [1:])

    def p_macro_call_element_list2 (self, p):
        'macro_call_element_list : macro_call_element_list macro_call_parens'
        p [0] = p [1]

    def p_macro_call_element_list3 (self, p):
        'macro_call_element_list : macro_call_parens'
        p [0] = ''

    def p_error(self, p):
        if p is not None:
            print("File: " + repr(self.filename) + " Line: " + str(self.lexer.lineno) + " Syntax error in input. Token type: %s, token value: %s, lex state: %s" % (p.type, p.value, self.lexer.lexstate))
        else:
            print("File: " + repr(self.filename) + " Line: " + str(self.lexer.lineno) + " Syntax error in input. Lex state: %s" % (self.lexer.lexstate,) )
        sys.exit (-1)
        
if __name__ == '__main__':

    text = """
enum global {earth, orb, globe};    
friend class whatever;
friend int max (int a, int b);

namespace foo
{    
enum fooEnum {apples, peaches, pumpkin_pie};
class bar
{
public:
    bar ();
    int baz ();
    int baz (double, long);
    QString method (int foo = 0);
    bar (int);
    bar (int, QList<QString>);
using dont care what;
enum barEnum {
    peas,
    carrots,
    beans
    } veggies;
typedef global::qint inttype;    
};
typedef enum elaborated something;
typedef enum simple {easy, bobsyouruncle, noproblem};
typedef QList<QPair<QString,QString>> stringpairlist;
typedef QString& stringref;
typedef QObject* objPtr;
typedef QObject** objPtrPtr;
typedef QString*& reftoStringPtr;
enum tail {end, posterior, ass};
}
    int baz ();
    virtual int baz (double);
    int baz (double, long long);
    int baz (double, long, unsigned long = ulong);
    virtual const QString& method (int foo = 0) = 0;
    QString method (int foo = 0, long fool = 20);
    bar (int a[40]);
    bar (int, QList<QString>);
    char* tmpl (QPair<QString, QString*> pair, const int foo);
    const char* string (QObject* object = QObject::type ());
    int varInt;
    double varDbl1, varDb12;
    QString s = 25;
    bar (int);
    bar (int a[40]);
    char *c[10];
    typedef void (* fptr)(int, double*);
    typedef int (* otherptr)();
    Q_OBJECT
    Q_SETS (who cares)
    double (*doublePtr)(float, QString*);
    bool test (int, int);
    bool operator == (int);
    int operator + (double);
    int operator >> (int);
    bool operator <<= (int a, int b);
    double (*doublePtr)();
    void* foo (int, double (*doublePtr)(float, QString*));
    void* foo (int, double (*doublePtr)());
    Q_DECLARE_FLAGS (Conditions, Condition)
    void plug () {
x = 1;
     y = 2;
}
class kdecore::KAccel raise (class QWidget elab) {
xyzabc = 1;
     y = 2;
     {
     if (x)
     {
        abc = 12;
     }
     }
     {
     while 1:
         x = 0;
     }
       
}
    """
    text = """

namespace Soprano {

    class Model;

    namespace Client {

        class DBusModel;

        /**
         * \class DBusClient dbusclient.h Soprano/Client/DBusClient
         *
         * \brief Core class to handle a connection to a Soprano server through the
         * DBus interface.
         *
         * DBusClient creates a connection to a running Soprano Server via its DBus
         * interface. All DBus communication is handled internally.
         *
         * See DBusModel for details about thread-safety.
         *
         * \author Sebastian Trueg <trueg@kde.org>
         *
         * \sa \ref soprano_server_dbus
         */
        class DBusClient : public QObject, public Error::ErrorCache
        {
            
       };
    }
}

"""
    text = """
    class Foo {
    public:
        const KTimeZone::Transition *transition(const QDateTime &dt, const Transition **secondTransition = 0, bool *validTime = 0) const;
};
"""
    
    from symboldata import Data
    from stateInfo import StateInfo

    symbolData = Data ()
    stateInfo  = StateInfo ()
    parser = CppParser ()
#    print "\n".join (parser.parse (symbolData, stateInfo, text, 2) [1])
    parser.parse (symbolData, stateInfo, text, 2)
