# -*- coding: utf-8 -*-
#     Copyright 2007-8 Jim Bublitz <jbublitz@nwinternet.com>
#     Copyright 2008   Simon Edwards <simon@simonzone.com>
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
import ply.yacc as yacc
from siplexer import sipLexer, tokens, setStateInfoTarget
from symboldata import NamespaceObject, ClassObject, EnumObject, Enumerator, TypedefObject
from symboldata import FunctionObject, Argument, VariableObject, EndClassMarker, EndNamespaceMarker
from symboldata import SipDirectiveObject, SipBlockObject, SipTypeObject, Template

class SipParser:
    def __init__ (self, testing = False):
        self.lexer       = sipLexer
        self.lexer.begin ('variable')
        self.testing     = testing
        self.test        = []
        self.arguments   = []
        self.annotation  = []
        self.versionLow  = ""
        self.versionHigh = ""
        self.platform    = ""
        self.ignore      = False
        self.templateParams = []
        self.template       = None
        
        self.tokens = tokens        
        yacc.yacc (module = self, tabmodule = "sipParserTab")
        self._parse = yacc.parse 
                    
    def parse (self, symbolData, stateInfo, text, debugLevel = 1, filename=None):
        self.symbolData = symbolData
        self.stateInfo  = stateInfo
        self.stateInfo.previousObject = None
        self.test       = []
        self.filename   = filename
        setStateInfoTarget (stateInfo)
        sipLexer.input (text)
        sipLexer.lineno = 1
        sipLexer.lexpos = 0
    
        result = self._parse (debug = debugLevel, lexer = self.lexer)

        if self.testing:
            return result, self.test
        else:
            return result
 
    def object_id_list (self, id_list, obj, objType = None):
        idList = id_list.split (',')
        if self.stateInfo.inTypedef:
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
        class_ = ClassObject (name, self.lexer.lineno, self.stateInfo)
        class_.templateParams = self.stateInfo.inTemplate
        class_.filepath = self.filename
        self.stateInfo.inTemplate = []
        self.stateInfo.pushClass (name, class_)
        if type_ == 'class':
            self.stateInfo.access = 'private'
        else:
            self.stateInfo.access = 'public'
        self.symbolData.objectList.append (class_)
        self.ignore = False
            
    def enumObject (self, name):
        enum = EnumObject (name, self.lexer.lineno, self.stateInfo)
        enum.filepath = self.filename
        
        self.lexer.begin ('enum')

        self.stateInfo.pushObject (enum)
        self.symbolData.objectList.append (enum)
        self.ignore = False
        
    def typedefObject (self, typeName, newName):
        typedefObj = TypedefObject (newName, self.lexer.lineno, self.stateInfo)
        typedefObj.filepath = self.filename
        typedefObj.setArgumentType (typeName)
        self.stateInfo.pushObject (typedefObj)
        self.symbolData.objectList.append (typedefObj)
        self.ignore = False
            
        return typedefObj

    def variableObject (self):
        v = self.arguments [0]
        varObj = VariableObject (v [1], self.lexer.lineno, self.stateInfo)
        varObj.variable = Argument (v [0], v [1], v [2], None, self.template)
        varObj.annotation = self.annotation
        varObj.filepath = self.filename
        self.stateInfo.pushObject (varObj)
        self.template   = None
        self.arguments  = []
        self.annotation = []
        self.symbolData.objectList.append (varObj)
        self.ignore = False
            
        return varObj
    
    def functionObject (self, name, returns):
        functionObj  = FunctionObject (name, self.lexer.lineno, self.stateInfo, returns == 'ctor')
        returnArg = Argument (returns)
        functionObj.returns.append (returnArg)
        functionObj.templateParams = self.stateInfo.inTemplate
        functionObj.filepath = self.filename
        self.stateInfo.inTemplate = []
        self.ignore = False
        
        self.stateInfo.pushObject (functionObj)
        self.symbolData.objectList.append (functionObj)

        self.lexer.begin ('function')

        return functionObj
        
    def argument (self, argumentType, argumentName = None, argumentValue = None, annotation = []):
        self.arguments.append ((argumentType, argumentName, argumentValue, annotation, None, None))        
        return self.arguments

    def setArguments (self, cpp = False, ctor = False):
        if not cpp:
            self.stateInfo.currentObject ().setArguments (self.arguments)
        else:
            self.stateInfo.currentObject ().setCppArgs (self.arguments, ctor)
        self.stateInfo.currentObject ().annotation = self.annotation
        self.arguments  = []
        self.annotation = []
        
    def sipDirectiveObject (self, name, arg):
        obj = SipDirectiveObject (name, self.lexer.lineno, self.stateInfo)
        obj.argument = arg
        self.symbolData.objectList.append (obj)

        
    precedence = (('left','PLUS','MINUS'), ('left','ASTERISK','SLASH'), ('right','UMINUS'), )
    
    # start
    def p_declarations (self, p):
        """declarations : member
                        | member_list member
                        | empty"""
        pass
        
    def p_member (self, p):
        """member : namespace_decl
                  | class_decl
                  | enum_decl
                  | typedef_decl
                  | function_decl
                  | variable_decl
                  | template_decl
                  | sip_stmt
                  | sip_block
                  | cmodule
                  | comp_module
                  | cons_module
                  | sip_end
                  | feature
                  | plugin
                  | defaultencoding
                  | defaultmetatype
                  | defaultsupertype
                  | sip_if
                  | import
                  | include
                  | license
                  | module
                  | optional_include
                  | platforms
                  | sipOptions
                  | timeline
                  | object_ignore
                  | object_force
                  | object_end"""
               
        self.lexer.begin (self.stateInfo.lexState)
        self.stateInfo.lexState  = 'variable'
        self.stateInfo.inTypedef = False
        self.stateInfo.ignore    = self.ignore           
        self.arguments  = []
        self.annotation = []
                  
    def p_member_list (self, p):
        """member_list : member
                       | member_list member"""
        pass

    def p_namespace_decl (self, p):
        'namespace_decl : namespace_name LBRACE member_list RBRACE SEMI'
        name, obj = self.stateInfo.popNamespace ()
        self.symbolData.objectList.append (EndNamespaceMarker (name, self.lexer.lineno, self.stateInfo))
        
    def p_namespace_decl1 (self, p):
        'namespace_decl : namespace_name SEMI'
        self.stateInfo.popNamespace ()
        self.ignore = False
        
    def p_namespace_name (self, p):
        'namespace_name : namespace ID'
        name = p [2]
        namespace = NamespaceObject (name, self.lexer.lineno, self.stateInfo)
        self.stateInfo.pushNamespace (name, namespace)
        self.symbolData.objectList.append (namespace)
        if self.testing:
            self.test.append ("namespace %s" % name)
        
    def p_empty (self, p):
        'empty :'
        pass
 
    def p_stmt_end (self, p):
        """stmt_end : SEMI"""
        pass

    def p_annotation_element (self, p):
        """annotation_element : ID
                              | ID EQUALS ID
                              | ID EQUALS ICONST
                              | ID EQUALS SCONST
                              | ID EQUALS HEXCONST"""
                      
        self.annotation.append (''.join (p [1:]))
        
    def p_annotation_list (self, p):
        """annotation_list : annotation_element
                           | annotation_list COMMA annotation_element"""
        pass
        
    def p_annotation (self, p):
        'annotation : SLASH annotation_list SLASH'
        pass

    def p_class_decl0 (self, p):
        """class_decl : class_header class_member_list RBRACE stmt_end
                      | opaque_class"""
        name, obj = self.stateInfo.popClass ()
        if not obj.opaque:
            self.symbolData.objectList.append (EndClassMarker (name, self.lexer.lineno, self.stateInfo))

    def p_class_decl1 (self, p):
        'class_decl : class_header class_member_list RBRACE id_list stmt_end'
        if p [1] in ['class', 'struct', 'union']:
            self.object_id_list (p [4], p [1])
        else:
            self.object_id_list (p [4], 'class')
        name, obj = self.stateInfo.popClass ()
        self.symbolData.objectList.append (EndClassMarker (name, self.lexer.lineno, self.stateInfo))
        
    def p_class_member (self, p):
        """class_member : class_decl
                        | enum_decl
                        | typedef_decl
                        | access_specifier
                        | function_decl
                        | variable_decl
                        | template_decl
                        | sip_stmt
                        | sip_block
                        | sip_end
                        | sip_if
                        | object_ignore
                        | object_force
                        | object_end"""

        self.lexer.begin (self.stateInfo.lexState)
        self.stateInfo.lexState  = 'variable'
        self.stateInfo.inTypedef = False
        self.stateInfo.ignore    = self.ignore          
        self.arguments  = []
        self.template   = None
            
    def p_access_specifier (self, p):
        """access_specifier : public COLON
                            | public slots COLON
                            | protected COLON
                            | protected slots COLON
                            | private COLON
                            | signals COLON
                            | slots COLON"""
                            
        self.stateInfo.access = p [1]

    def p_class_member_list (self, p):
        """class_member_list : class_member
                             | class_member_list class_member"""
        pass

    
    def p_class_header0 (self, p):
        """class_header : class_name LBRACE
                        | class_name COLON base_list LBRACE"""
        p [0] = p [1]
    
    def p_class_header1 (self, p):
        """class_header : class_name annotation LBRACE
                        | class_name COLON base_list annotation LBRACE"""
        p [0] = p [1]
        self.stateInfo.currentObject ().annotation = self.annotation
        self.annotation = []
        
    def p_class_name (self, p):
        """class_name : class ID
                      | struct ID
                      | union ID"""
        self.classObject (p [2], p [1])
            
    def p_opaque_class (self, p):
        """opaque_class : class qualified_id SEMI
                        | class qualified_id annotation SEMI
                        | class_name SEMI
                        | class_name annotation SEMI"""
        self.stateInfo.currentObject ().opaque = True
        
    
    def p_base_list_element (self, p):
        'base_list_element : qualified_id'
        self.stateInfo.currentObject ().bases.append (p [1])
     
    def p_base_list (self, p):
        """base_list : base_list_element
                     | base_list COMMA base_list_element"""
        pass
       
    def p_enum_decl0 (self, p):
        'enum_decl : enum_statement SEMI'
        self.stateInfo.popObject ()
        
    def p_enum_decl1 (self, p):
        'enum_decl : enum_statement id_list SEMI'
        self.object_id_list (p [2], 'enum')
        self.stateInfo.popObject ()
        
    def p_enum_statement (self, p):
        """enum_statement : enum_name enumerator_list RBRACE
                          | enum_name enumerator_list COMMA RBRACE
                          | enum_name RBRACE"""
        pass
        
    def p_enum_name0 (self, p):
        """enum_name : enum ID LBRACE
                     | enum LBRACE"""                     
            
        if p[2] != "{":
            name = p [2]
        else:
            name = 'anonymous'
        self.enumObject (name)
                    
    def p_enumerator (self, p):
        """enumerator : ID
                      | ID ENUMINIT"""
                
        if len (p) == 3:
            enumerator = Enumerator (p [1], p [2], self.stateInfo)
        else:
            enumerator = Enumerator (p [1], None, self.stateInfo)
            
        self.stateInfo.currentObject ().enumerators.append (enumerator)
        if self.testing:
            self.test.append (enumerator.name)
            
    def p_versioned_enumerator_start (self, p):
        'versioned_enumerator_start : sip_if enumerator'
        pass
        
    def p_versioned_enumerator_list (self, p):
        """versioned_enumerator_list : versioned_enumerator_start   
                                                 | versioned_enumerator_start COMMA
                                                 | versioned_enumerator_list enumerator
                                                 | versioned_enumerator_list enumerator COMMA"""
        pass
        
    def p_versioned_enumerator_block (self, p):
        'versioned_enumerator_block : versioned_enumerator_list sip_end'
        pass
            
    
    def p_enumerator_list (self, p):
        """enumerator_list : enumerator
                                   | versioned_enumerator_block
                                   | versioned_enumerator_block enumerator
                                   | enumerator_list COMMA enumerator
                                   | enumerator_list COMMA versioned_enumerator_block
                                   | enumerator_list COMMA versioned_enumerator_block enumerator
                                   | enumerator_list versioned_enumerator_block
                                   | enumerator_list versioned_enumerator_block enumerator"""
        pass
        
    def p_id_list_element (self, p):
        'id_list_element : ID'
        p [0] = p [1]
        
    def p_id_list (self, p):
        """id_list : id_list_element
                   | id_list COMMA id_list_element"""
        p [0] = "".join (p [1:])
                   
    def p_qualified_id (self, p):
        """qualified_id : ID
                        | nested_name_specifier"""
        p [0] = p [1]
                        
    def p_nested_name_specifier (self, p):
        """nested_name_specifier : ID COLON2 ID
                                 | nested_name_specifier COLON2 ID
                                 | template_type COLON2 ID"""
        p [0] = "".join (p [1:])
        
    def p_template_type (self, p):
        'template_type : qualified_id LT type_specifier_list GT'
        p [0] = "".join (p [1:])
        self.template = Template (p [1], p [3], self.template)
       
    def p_elaborated_type (self, p):
        """elaborated_type : enum qualified_id
                          | class qualified_id
                          | struct qualified_id
                          | union qualified_id"""
        p [0] = '%s %s' % (p [1], p [2])
    
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
                               | signed long
                               | signed long int
                               | long long
                               | unsigned long long
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
        
    def p_type_decorator (self, p):
        """type_decorator : ASTERISK
                          | AMPERSAND
                          | ASTERISK AMPERSAND
                          | ASTERISK ASTERISK
                          | ASTERISK ASTERISK ASTERISK"""
        p [0] = "".join (p [1:])
        
    def p_type_specifier_list (self, p):
        """type_specifier_list : type_specifier
                               | type_specifier_list COMMA type_specifier"""
        p [0] = "".join (p [1:])
                   
    def p_typedef_decl (self, p):
        """typedef_decl : typedef_simple SEMI
                        | typedef_simple annotation SEMI
                        | typedef_function_ptr SEMI"""
        self.stateInfo.popObject ()
       
    def p_typedef_simple (self, p):
        'typedef_simple : typedef type_specifier ID'
        self.typedefObject (p [2], p [3])
        self.stateInfo.inTypedef = True
                                        
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
        if self.testing:
            self.test.append ('typedef p-t-f %s %s %s' % (ptrType, name, typedefObj.functionPtr))
        self.stateInfo.inTypedef = True
        
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
        p [0] = self.argument ('$fp' + argType, name, args)
        
    def p_argument_specifier5 (self, p):
        'argument_specifier : type_specifier annotation'
        p [0] = self.argument (p [1], None, None, self.annotation)
        self.annotation  = []
        
    def p_argument_specifier6 (self, p):
        'argument_specifier : type_specifier ID annotation'
        p [0] = self.argument (p [1], p [2], None, self.annotation)
        self.annotation = []
        
    def p_argument_specifier7 (self, p):
        'argument_specifier : type_specifier annotation EQUALS expression'
        p [0] = self.argument (p [1], None, p [4], self.annotation)
        self.annotation = []
               
    def p_argument_specifier8 (self, p):
        'argument_specifier : type_specifier ID annotation EQUALS expression'
        p [0] = self.argument (p [1], p [2], p [5], self.annotation)
        self.annotation = []
                              
    def p_argument_list0 (self, p):
        """argument_list : argument_specifier"""
        p [0] = [p [1]]
        
    def p_argument_list1 (self, p):
        """argument_list : argument_list COMMA argument_specifier
                         | argument_list COMMA type_specifier"""
        if p [0]:
            p [0].append (p [3])
        else:
            p [0] = [p [3]]
            
    def p_exception_element (self, p):
        'exception_element : qualified_id'
        p [0] = p [1]
        
    def p_exception_list (self, p):
        """exception_list : exception_element
                          | exception_list COMMA exception_element"""
        p [0] = "".join (p [1:])
        
    def p_exception (self, p):
        'exception : throw LPAREN exception_list RPAREN'
        self.stateInfo.currentObject ().exceptions = p [3]       

    def p_variable_decl0 (self, p):
        """variable_decl : argument_specifier SEMI
                         | argument_specifier annotation SEMI"""
        self.variableObject () 
        self.stateInfo.popObject ()
                         
    def p_variable_decl1 (self, p):
        """variable_decl : STORAGE argument_specifier SEMI
                         | STORAGE argument_specifier annotation SEMI"""
                         
        varObj = self.variableObject () 
        varObj.variable.attributes.storageClass = p [1]
        self.stateInfo.popObject ()
                
    def p_function_name0 (self, p):
        'function_name : type_specifier ID LPAREN'
        self.functionObject (p [2], p[1])
        self.arguments = []
        
    def p_function_name1 (self, p):
        'function_name : STORAGE type_specifier ID LPAREN'
        fObj = self.functionObject (p [3], p[2])
        self.arguments = []
        fObj.attributes.storageClass = p [1]

    def p_operator_pfx (self, p):
        'operator_pfx : type_specifier operator'
        p [0] = p [1]
        
    def p_cast_operator_name0 (self, p):
        'cast_operator_name : operator type_specifier LPAREN RPAREN'
        self.functionObject ('operator ' + p [2], p[2])
        self.arguments  = []
        
    def p_cast_operator_name1 (self, p):
        'cast_operator_name : operator type_specifier LPAREN RPAREN CVQUAL'
        fObj = self.functionObject ('operator ' + p [2], p[2])
        fObj.attributes.cv = p [5]
        self.arguments  = []        
        
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
                         | operator_pfx CARET LPAREN
                         | operator_pfx TILDE LPAREN
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
                         | operator_pfx CARET EQUALS LPAREN
                         | operator_pfx PLUSPLUS LPAREN
                         | operator_pfx MINUSMINUS LPAREN
                         | operator_pfx ARRAYOP LPAREN
                         | operator_pfx LPAREN RPAREN LPAREN
                         | operator_pfx ARROW LPAREN
                         | operator_pfx NE LPAREN"""
        n = len (p) - 1
        self.functionObject ('operator ' + "".join (p [2:n]), p[1])
        self.arguments  = []
        
    def p_operator_primary0 (self, p):
        """operator_primary : operator_name argument_list RPAREN
                            | operator_name RPAREN
                            | cast_operator_name"""
        self.setArguments ()
        if self.testing:
            self.test.append (str (self.arguments))

    def p_operator_primary1 (self, p):
        """operator_primary : virtual operator_name argument_list RPAREN
                            | virtual operator_name RPAREN
                            | virtual cast_operator_name"""
        self.setArguments ()
        self.stateInfo.currentObject ().attributes.functionQualifer = 'virtual'
        if self.testing:
            self.test.append (str (self.arguments))

    def p_operator_stmt0 (self, p):
        """operator_stmt : operator_primary SEMI
                         | operator_primary exception SEMI
                         | operator_primary annotation SEMI
                         | operator_primary exception annotation SEMI
                         | operator_primary cpp_args SEMI
                         | operator_primary exception cpp_args SEMI
                         | operator_primary annotation cpp_args  SEMI
                         | operator_primary exception annotation cpp_args SEMI"""
        self.setArguments (True)
        
    def p_operator_stmt1 (self, p):
        """operator_stmt : operator_primary CVQUAL SEMI
                         | operator_primary CVQUAL exception SEMI
                         | operator_primary CVQUAL annotation SEMI
                         | operator_primary CVQUAL exception annotation SEMI
                         | operator_primary CVQUAL cpp_args SEMI
                         | operator_primary CVQUAL exception cpp_args SEMI
                         | operator_primary CVQUAL annotation cpp_args SEMI
                         | operator_primary CVQUAL exception annotation cpp_args SEMI"""
        self.setArguments (True)
        self.stateInfo.currentObject ().attributes.cv = p [2]

    def p_ctor_name0 (self, p):
        'ctor_name : ID LPAREN'
        self.functionObject (p [1], 'ctor')
        self.arguments = []
        
    def p_ctor_name1 (self, p):
        'ctor_name : explicit ID LPAREN'
        fo = self.functionObject (p [2], 'ctor')
        fo.attributes.functionQualifier = 'explicit'
        self.arguments = []

    def p_dtor_name (self, p):
        'dtor_name : TILDE ID'
        self.functionObject (p [2], 'dtor')
        self.arguments = []
        
    def p_virtual_dtor_name (self, p):
        'virtual_dtor_name : virtual dtor_name'
        self.arguments = []
                            
    def p_function_decl (self, p):
        """function_decl : ctor_stmt
                         | dtor_stmt
                         | function_stmt
                         | operator_stmt
                         | virtual_stmt
                         | pure_virtual"""
        self.stateInfo.popObject ()
                                 
    def p_function_primary (self, p):
        """function_primary : function_name RPAREN
                            | function_name argument_list RPAREN"""
                            
        self.setArguments ()
        if self.testing:
            self.test.append (str (self.arguments))
            
    def p_function_primary (self, p):
        """function_primary : function_name RPAREN
                            | function_name argument_list RPAREN"""
                            
        self.setArguments ()
        if self.testing:
            self.test.append (str (self.arguments))
 
    def p_cpp_args (self, p):
        'cpp_args : LBRACKET type_specifier cpp_arg_list RBRACKET'
        self.arguments.insert (0, (p [2], None, None, None, None, None))
        pass
        
    def p_cpp_arg_list (self, p):
        """cpp_arg_list : LPAREN argument_list RPAREN
                        | LPAREN RPAREN"""
        pass
        
    def p_cpp_ctor_args (self, p):
        'cpp_ctor_args : LBRACKET cpp_arg_list RBRACKET'
        pass
                
    def p_function_stmt0 (self, p):
        """function_stmt : function_primary stmt_end
                         | function_primary exception stmt_end
                         | function_primary annotation stmt_end
                         | function_primary exception annotation stmt_end
                         | function_primary cpp_args stmt_end
                         | function_primary exception cpp_args stmt_end
                         | function_primary annotation cpp_args stmt_end
                         | function_primary exception annotation cpp_args stmt_end"""
        self.setArguments (True)
        
    def p_function_stmt1 (self, p):
        """function_stmt : function_primary CVQUAL stmt_end
                         | function_primary CVQUAL exception stmt_end
                         | function_primary CVQUAL annotation stmt_end
                         | function_primary CVQUAL exception annotation stmt_end
                         | function_primary CVQUAL cpp_args stmt_end
                         | function_primary CVQUAL exception cpp_args stmt_end
                         | function_primary CVQUAL annotation cpp_args stmt_end
                         | function_primary CVQUAL exception annotation cpp_args stmt_end"""
        self.stateInfo.currentObject ().attributes.cv = p [2]
        self.setArguments (True)
        
    def p_function_stmt2 (self, p):
        'function_stmt : function_primary EQUALS ICONST stmt_end'
        self.setArguments (True)
        self.stateInfo.currentObject ().attributes.functionQualifier = 'virtual'
    def p_ctor_primary (self, p):
        """ctor_primary : ctor_name RPAREN
                        | ctor_name argument_list RPAREN"""                        
        self.setArguments (False, True)
        if self.testing:
            self.test.append (str (self.arguments))
        
    def p_ctor_stmt (self, p):
        """ctor_stmt : ctor_primary stmt_end
                     | ctor_primary annotation stmt_end
                     | ctor_primary cpp_ctor_args stmt_end
                     | ctor_primary annotation cpp_ctor_args stmt_end"""
        self.setArguments (True, True)
        
    def p_dtor_primary0 (self, p):
        'dtor_primary : dtor_name LPAREN RPAREN'
        pass
        
    def p_dtor_primary1 (self, p):
        'dtor_primary : virtual_dtor_name LPAREN RPAREN'
        self.stateInfo.currentObject ().attributes.functionQualifier = 'virtual'
        
    def p_dtor_stmt (self, p):
        'dtor_stmt : dtor_primary stmt_end'
        pass
        
    def p_virtual_primary (self, p):
        """virtual_primary : virtual function_name RPAREN
                           | virtual function_name argument_list RPAREN
                           | STORAGE virtual function_name RPAREN
                           | STORAGE virtual function_name argument_list RPAREN"""
        self.setArguments ()
        if p [1] != 'virtual':
            self.stateInfo.currentObject ().attributes.storageClass = p [1]
            
        
    def p_virtual_stmt0 (self, p):
        """virtual_stmt : virtual_primary SEMI
                        | virtual_primary exception SEMI"""
        self.stateInfo.currentObject ().attributes.functionQualifier = 'virtual'

    def p_virtual_stmt1 (self, p):
        """virtual_stmt : virtual_primary CVQUAL SEMI
                        | virtual_primary CVQUAL exception SEMI"""
        self.stateInfo.currentObject ().attributes.functionQualifier = 'virtual'
        self.stateInfo.currentObject ().attributes.cv = p [2]

    def p_virtual_stmt2 (self, p):
        """virtual_stmt : virtual_primary annotation SEMI
                        | virtual_primary annotation cpp_args SEMI
                        | virtual_primary cpp_args SEMI
                        | virtual_primary exception annotation SEMI
                        | virtual_primary exception annotation cpp_args SEMI
                        | virtual_primary exception cpp_args SEMI"""
        self.setArguments (True)
        self.stateInfo.currentObject ().attributes.functionQualifier = 'virtual'

    def p_virtual_stmt3 (self, p):
        """virtual_stmt : virtual_primary CVQUAL annotation SEMI
                        | virtual_primary CVQUAL annotation cpp_args SEMI
                        | virtual_primary CVQUAL cpp_args SEMI
                        | virtual_primary CVQUAL exception annotation SEMI
                        | virtual_primary CVQUAL exception annotation cpp_args SEMI
                        | virtual_primary CVQUAL exception cpp_args SEMI"""
        self.setArguments (True)
        self.stateInfo.currentObject ().attributes.functionQualifier = 'virtual'
        self.stateInfo.currentObject ().attributes.cv = p [2]
        
    def p_pure_virtual_suffix (self, p):
        """pure_virtual_suffix : EQUALS ICONST
                               | EQUALS ICONST annotation
                               | EQUALS ICONST annotation cpp_args
                               | EQUALS ICONST cpp_args"""
        self.setArguments (True)

    def p_pure_virtual (self, p):
        """pure_virtual : virtual_primary pure_virtual_suffix SEMI
                        | virtual_primary CVQUAL pure_virtual_suffix SEMI
                        | virtual_primary exception pure_virtual_suffix SEMI
                        | virtual_primary CVQUAL exception pure_virtual_suffix SEMI"""
        self.stateInfo.currentObject ().attributes.functionQualifier = 'pure'
        if p [2] in ['const', 'volatile']:
            self.stateInfo.currentObject ().attributes.cv = p [2]
        
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
        self.stateInfo.inTemplate = ', '.join (self.templateParams)
        self.templateParams = []

##    def p_template_decl (self, p):
##        'template_decl : template LT type_specifier_list GT'
##        self.stateInfo.inTemplate = p [3]
        
    def p_sip_block (self, p):
        'sip_block : sip_block_header BLOCK_BODY'
        blockObj = SipBlockObject (p [1], self.lexer.lineno, self.stateInfo)
        blockObj.block = ('\n'.join (p [1:])) 
        if self.stateInfo.previousObject:
            self.stateInfo.previousObject.blocks.append (blockObj)
        else:
            self.symbolData.objectList.append (blockObj)

    def p_sip_block_header (self, p):
        'sip_block_header : PERCENT BLOCK'
        p [0] = ''.join (p [1:])

    def p_sip_stmt (self, p):
        'sip_stmt : sip_stmt_header SIPSTMT_BODY'
        p [0] = '\n'.join (p [1:])
        self.stateInfo.currentObject ().block = ('\n'.join (p [1:]))        
        
    def p_sip_stmt_header (self, p):
        """sip_stmt_header : PERCENT SIPSTMT type_specifier
                           | PERCENT SIPSTMT qualified_id LPAREN qualified_id RPAREN"""
        p [0] = '%%%s %s' % (p [2], ''.join (p [3:]))
        sipTypeObj = SipTypeObject (p [3], self.lexer.lineno, self.stateInfo, p [2])
        if len (p) == 7:
            sipTypeObj.base = p [5]
        if self.stateInfo.inTemplate:
            sipTypeObj.templateParams = self.stateInfo.inTemplate
            sipTypeObj.template       = self.template
            self.stateInfo.inTemplate = []
        self.symbolData.objectList.append (sipTypeObj)
        self.stateInfo.pushObject (sipTypeObj)
                
    def p_cmodule (self, p):
        """cmodule : PERCENT CModule ID
                   | PERCENT CModule ID ICONST"""
        self.sipDirectiveObject ('CModule', ",".join (p [2:]))

    def p_comp_module (self, p):
        'comp_module : PERCENT CompositeModule ID'
        self.sipDirectiveObject ('CompositeModule', p [2])

    def p_cons_module (self, p):
        'cons_module : PERCENT ConsolidatedModule ID'
        self.sipDirectiveObject ('ConsolidatedModule', p [2])
        
    def p_feature (self, p):
        'feature : PERCENT Feature ID'
        self.sipDirectiveObject ('Feature', p [3])

    def p_plugin (self, p):
        'plugin : PERCENT Plugin ID'
        self.sipDirectiveObject ('Plugin', p [3])

    def p_defaultencoding (self, p):
        'defaultencoding : PERCENT DefaultEncoding STRING'

    def p_defaultmetatype (self, p):
        'defaultmetatype : PERCENT DefaultMetatype DOTTEDNAME'

    def p_defaultsupertype (self, p):
        'defaultsupertype : PERCENT DefaultSupertype DOTTEDNAME'

    def p_if_expression (self, p):
        """if_expression : ored_qualifiers
                         | range"""
        self.stateInfo.pushVersion ((self.versionLow, self.versionHigh, self.platform))

    def p_ored_qualifiers (self, p):
        """ored_qualifiers : if_qualifier
                           | ored_qualifiers VBAR VBAR if_qualifier
                           | ored_qualifiers LOR if_qualifier"""
        p [0] = "".join (p [1:]) 
        self.platform = p [0]

    def p_if_qualifier (self, p):
        """if_qualifier : ID
                        | BANG ID"""
        p [0] = p [1]

    def p_range0 (self, p):
        'range : ID MINUS'
        self.versionLow  = p [1]
        self.versionHigh = ''
        
    def p_range1 (self, p):
        'range : MINUS ID'
        self.versionHigh = p [2]
        self.versionLow  = ''
        
    def p_range2 (self, p):
        'range : ID MINUS ID'
        self.versionLow  = p [1]
        self.versionHigh = p [3]
        
    def p_sip_if (self, p):
        """sip_if : PERCENT If LPAREN if_expression RPAREN"""
        pass
        
    def p_sip_end (self, p):
        'sip_end : PERCENT End'
        self.versionLow, self.versionHigh, self.platform = self.stateInfo.popVersion ()

    def p_import (self, p):
        'import : PERCENT Import FILENAME'
        self.sipDirectiveObject ('Import', p [3])
        
    def p_include (self, p):
        'include : PERCENT Include FILENAME'
        self.sipDirectiveObject ('Include', p [3])
        
    def p_license_annot (self, p):
        'license_annot : licenseAnnotation'
        p [0] = p [1]
        
    def p_license_annot_list (self, p):
        """license_annot_list : license_annot
                              | license_annot_list COMMA license_annot"""
        p [0] = "".join (p [1:])
        
    def p_license (self, p):
        'license : PERCENT License SLASH license_annot_list SLASH'
        self.sipDirectiveObject ('License', p [4])
        
    def p_module (self, p):
        """module : PERCENT Module FILENAME
                  | PERCENT Module FILENAME ICONST"""
        self.sipDirectiveObject ('Module', ",".join (p [3:]))
                  
    def p_optional_include (self, p):
        'optional_include : PERCENT OptionalInclude FILENAME'
        self.sipDirectiveObject ('OptionalInclude', p [3])

    def p_undelimited_id_list (self, p):
        """undelimited_id_list : ID
                               | undelimited_id_list ID"""
        p [0] = " ".join (p [1:])
        
    def p_platforms (self, p):
        'platforms : PERCENT Platforms LBRACE undelimited_id_list RBRACE'
        self.sipDirectiveObject ('Platforms', p [4])
        
    def p_sipOptions (self, p):
        'sipOptions : PERCENT SIPOptions LPAREN id_list RPAREN'
        self.sipDirectiveObject ('SIPOptions', p [4])
                    
    def p_timeline (self, p):
        'timeline : PERCENT Timeline LBRACE undelimited_id_list RBRACE'
        self.sipDirectiveObject ('Timeline', p [4])
        
    def p_object_ignore (self, p):
        'object_ignore : IG'
        self.ignore = True

    def p_object_force (self, p):
        'object_force : FORCE'
        self.stateInfo.force = True

    def p_object_end (self, p):
        'object_end : END'
        self.stateInfo.force = False

# expression handling for argument default values - just parses and
# then reassembles the default value expression (no evaluation)

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
    
    def p_expression3 (self, p):
        """expression : type_specifier LPAREN expression_list RPAREN
                      | type_specifier LPAREN RPAREN"""
        p [0] = "".join (p [1:])
        
    def p_expression_list (self, p):
        """expression_list : expression
                           | expression_list COMMA expression"""
        p [0] = "".join (p [1:])

    def p_unary_expression (self, p):
        """unary_expression : sign_expression
                            | not_expression
                            | bitnot_expression"""
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

    def p_error(self, p):
        print "sip parser ..."
        filename = self.filename if self.filename is not None else "(?)"
        print "syntax error in file %s -- token type %s   token value %s   lex state" % (filename, p.type, p.value)#, p.lexer.lexstate)
        sys.exit (-1)

        
if __name__ == '__main__':

    text = """
enum global {earth, orb, globe};    

namespace foo
{    
enum fooEnum {apples, peaches, pumpkin_pie};
class bar
{
public:
    bar ();
    explict bar(int x);
    int baz ();
    int baz (double, long) [int (double, long)];
    QString method (int foo = 0);
    bar (int);
    bar (int, QList<QString>);
    QTextStream &operator<<(double f /Constrained/);
//    QTextStream &operator<<(bool b /Constrained/) [QTextStream & (QBool b /Constrained/)];
    QTextStream &foosiggy(bool b /Constrained/) [QTextStream & (QBool b /Constrained/)];

enum barEnum {
    peas,
    carrots,
    beans
    } veggies;
typedef global::qint inttype;    
};
typedef QList<QPair<QString,QString>> stringpairlist;
typedef QString& stringref;
typedef QObject* objPtr;
typedef QObject** objPtrPtr;
typedef QString*& reftoStringPtr;
enum tail {end, posterior, ass};
};
    int baz ();
    virtual int baz (double);
    int baz (double, long long);
    int baz (double, long, unsigned long = ulong);
    virtual const QString& method (int foo = 0) = 0;
    QString method (int foo = 0, long fool = 20);
    bar (int, QList<QString>);
    char* tmpl (QPair<QString, QString*> pair, const int foo);
    const char* string (QObject* object = QObject::type ());
    int varInt;
    bar (int);
    bar (int a[40]);
    char *c[10];
    typedef void (* fptr)(int, double*);
    typedef int (* otherptr)();
    bool test (int, int);
    bool operator == (int);
    int operator + (double);
    int operator >> (int);
    bool operator <<= (int a, int b);
    double (*doublePtr)();
    void* foo (int, double (*doublePtr)(float, QString*));
    void* foo (int, double (*doublePtr)());
    void plug ();
kdecore::KAccel raise (QWidget elab);
    typedef QList<QPair<int,QString*>>\
    (* seven)();
%MappedType FooBar
{
%ConvertToTypeCode
%End
%ConverFromTypeCode
%End
};
%AccessCode
something goes in here
for a few lines
%End
"""

    text = """
class bar
{
public:
    bar ();
    explict bar(int x);
;}
"""


#    text = """virtual bool operator<(const QListWidgetItem &other) const;
#    """
##    void update(const QRectF & = QRectF(0.0, 0.0, 1.0e+9, 1.0e+9));
##    static void singleShot(int msec, SIP_RXOBJ_CON receiver, SIP_SLOT_CON() member);    
##    %MappedType QList<TYPE>
##    QCoreApplication(SIP_PYLIST argv) /PostHook=__pyQtQAppHook/ [(int &argc, char **argv)];
##    mutable virtual KAccel raise (float** zero /In, Out/) volatile  throw (bar, baz)/PyName=foo_bar/;"""
##    virtual bool open(QFlags<QIODevice::OpenModeFlag> openMode) /ReleaseGIL/;
##    static QAbstractEventDispatcher *instance(QThread *thread = 0);
##    QFlags &operator^=(QFlags f);
##    %Timeline {Qt_4_1_0  Qt_4_1_1  Qt_4_1_2  Qt_4_2_0}
##    // hello - I'm a C++ comment
##    static virtual unsigned short has_icon (someEnum zero /Transfer/ = flags(abc) | flags(xyz)) volatile/PyName=foo_bar, Transfer/;
##    """

    
    from symboldata import Data
    from stateInfo import StateInfo

    symbolData = Data ()
    stateInfo  = StateInfo ()
    parser = SipParser (True)
    print "\n".join (parser.parse (symbolData, stateInfo, text, 2) [1])