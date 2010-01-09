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

import ply.lex as lex

class CppLexerClass(object):
    def __init__(self):
        self.codeStack = []
        self.parenStack = []
        self._bareMacros = []
        self._macros = []

    def setBareMacros(self,macroList):
        # macroList - List of strings
        self._bareMacros = macroList

    def setMacros(self,macroList):
        # macroList - List of strings
        self._macros = macroList

    states = (('function', 'inclusive'), ('macro', 'exclusive'), ('operator', 'inclusive'), ('variable', 'inclusive'),\
            ('stmt', 'exclusive'), ('enum', 'inclusive'))

    accessSpecifiers = ("private", "protected", "public", "slots", "signals")

    edges = ("class", "struct", "union",  "template", "enum", "namespace",\
            "typedef", "operator", 'typename')

    storageQualifiers = ("auto", "register", "static", "extern", "mutable")

    functionQualifiers = ("virtual",  "explicit")

    cvQualifiers = ("const", "volatile")

    cppScalarTypes = ("int", "char", "float", "double", "long", "short", "unsigned",\
        "signed", "bool", "void", "wchar_t")        

    # Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
    operators = ('PLUS', 'MINUS', 'SLASH', 'PERCENT', 'VBAR', 'CARET', #'LSHIFT', 'RSHIFT',
        'LOR', 'LAND', 'BANG', 'LE', 'GE', 'EQ', 'NE',
        # Increment/decrement (++,--)
        'PLUSPLUS', 'MINUSMINUS',
        # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
        'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
        'LSHIFTEQUAL',#'RSHIFTEQUAL', 
        'ANDEQUAL', 'XOREQUAL', 'OREQUAL', 'new', 'static_cast'
    )
    
    doc = ('DOC', 'UPDOC')

    tokens = accessSpecifiers + edges + functionQualifiers + cppScalarTypes + operators + doc + (
    # Literals (identifier, integer constant, float constant, string constant, char const)
    'ID', 'ICONST', 'HEXCONST', 'FCONST', 'SCONST', 'CCONST', 'CVQUAL',
    'STORAGE', 'PURESFX', 'CODE_TOKEN', 'STMT_BEGIN', 'STMT_END', 'CODE_STMT_BEGIN',

    # Expressions we don't parse
    'ARRAYOP', 'FUNCPTR', 'BAREMACRO', 'MACROCALL', 'MACRO_ELEMENT', 'MACRO_CALL_BEGIN', 'MACRO_CALL_END',

    # Structure dereference (->)
    'ARROW',

    # Treat separately from other operators
    'EQUALS', 'ASTERISK', 'AMPERSAND', 'TILDE', 'LT', 'GT',

    # Delimeters ( ) [ ] { } , . ; : ::
    'LPAREN', 'RPAREN',
    #'LBRACKET', 'RBRACKET',
    'LBRACE', 'RBRACE',
    'COMMA', 'PERIOD', 'SEMI', 'COLON', 'COLON2',

    # Ellipsis (...)
    'ELLIPSIS'
    )

    # Completely ignored characters
    t_ANY_ignore          = ' \t\x0c'
    #t_ANY_ignore_typename = 'typename'

    # Operators
    t_PLUS             = r'\+'
    t_MINUS            = r'-'
    t_ASTERISK         = r'\*'
    t_SLASH            = r'/'
    t_PERCENT          = r'%'
    t_VBAR             = r'\|'
    t_AMPERSAND        = r'&'
    t_TILDE            = r'~'
    t_CARET            = r'\^'
    #t_LSHIFT           = r'<<'
    #t_RSHIFT           = r'>>'
    t_LOR              = r'\|\|'
    t_LAND             = r'&&'
    t_BANG             = r'!'
    t_LT               = r'<'
    t_GT               = r'>'
    t_LE               = r'<='
    t_GE               = r'>='
    t_EQ               = r'=='
    t_NE               = r'!='

    # Assignment operators

    t_EQUALS           = r'='
    t_TIMESEQUAL       = r'\*='
    t_DIVEQUAL         = r'/='
    t_MODEQUAL         = r'%='
    t_PLUSEQUAL        = r'\+='
    t_MINUSEQUAL       = r'-='
    t_LSHIFTEQUAL      = r'<<='
    #t_RSHIFTEQUAL      = r'>>='
    t_ANDEQUAL         = r'&='
    t_OREQUAL          = r'\|='
    t_XOREQUAL         = r'^='

    # Increment/decrement
    t_PLUSPLUS         = r'\+\+'
    t_MINUSMINUS       = r'--'

    # ->
    t_ARROW            = r'->'

    # Delimeters
    t_LPAREN           = r'\('

    def t_macro_LPAREN(self,t):
        r'\('
        if not self.parenStack:
            t.type = 'MACRO_CALL_BEGIN'
            self.parenStack.append (True)
        else:
            t.type = 'LPAREN'
            self.parenStack.append (False)
            
        return t

    t_RPAREN           = r'\)'

    def t_macro_RPAREN(self,t):
        r'\)'
        if self.parenStack.pop ():
            t.type = 'MACRO_CALL_END'
            t.lexer.begin ('variable')
        else:
            t.type = 'RPAREN'
        return t
        
    def t_macro_MACRO_ELEMENT(self,t):
        r'[^\(\)\s]+'
        t.lexer.lineno += t.value.count ('\n')
        return t

    #t_LBRACKET         = r'\['
    #t_RBRACKET         = r'\]'

    def t_ANY_LBRACE(self,t):
        r'\{'
        if t.lexer.lexstate in ['operator', 'function']:
            t.type = 'STMT_BEGIN'
            self.codeStack.append (t.lexer.lexstate)
            t.lexer.begin ('stmt')
        elif t.lexer.lexstate == 'stmt':
            t.type = 'CODE_STMT_BEGIN'
            self.codeStack.append ('stmt')
        else:
            t.type = 'LBRACE'
        return t
            
    def t_ANY_RBRACE(self,t):
        r'\}'
        if t.lexer.lexstate in ['stmt', 'function', 'operator']:
            if self.codeStack:
                t.lexer.begin(self.codeStack.pop ())
                t.type = 'STMT_END'
            else:
                t.type = 'RBRACE'
        else:
            t.type = 'RBRACE'
        return t

    def t_stmt_CODE_TOKEN(self,t):
        r'[^{}\s]+'
        if '\n' in t.value:
            t.lexer.lineno += t.value.count ('\n')
        return t

    t_COMMA            = r','
    t_PERIOD           = r'\.'
    t_SEMI             = r';'
    t_COLON            = r':'
    t_ELLIPSIS         = r'\.\.\.'
    t_COLON2           = r'::'

    # Hex Literal
    def t_HEXCONST(self,t):
        r'0[x|X][\da-fA-F]+'
        t.type = 'HEXCONST'
        return t

    # Integer literal
    t_ICONST = r'\d+([uUlL])?([uUlL])?' #r'(0(?![x|X])|[1-9])\d*([uU]|[lL]|[uU][lL]|[lL][uU])?'

    # Floating literal
    t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

    t_function_PURESFX = r'0;'

    t_operator_PURESFX = r'0;'

    # Array operator
    t_ARRAYOP = r'[[].*[]]'

    # Function pointer
    t_FUNCPTR  = r'\(\s*\*'

    # String literal
    t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

    # Character constant 'c' or L'c'
    t_CCONST = r'(L)?\'([^\\\n]|(\\.))*?\''
    # Newlines

    # some things we ignore (entire line)
    def t_friend_class(self,t):
        r'friend\s+class\s+[^;]*;?'
        t.lexer.lineno += t.value.count("\n")

    def t_friend(self,t):
        r'friend\s'
        pass    

    def t_using(self,t):
        r'using\s+.*;?'
        t.lexer.lineno += t.value.count ('\n')

    def t_inline(self,t):
        r'inline\s+'

    def t_ANY_NEWLINE(self,t):
        r'(\\\n|\n)+'
        t.lexer.lineno += t.value.count("\n")
            
    def t_ID(self,t):
        r'[A-Za-z_][\w_]*'
        if t.value in ['class', 'namespace']:
            t.lexer.begin ('variable')
            
        if t.value in CppLexerClass.edges or t.value in ['new', 'static_cast']:
            t.type = t.value
            if t.type == 'operator':
                t.lexer.begin ('operator')
            if t.type == 'enum' and t.lexer.lexstate != 'function':
                t.lexer.begin ('enum')
        elif t.value in CppLexerClass.cppScalarTypes:
            t.type = t.value
        elif t.value in CppLexerClass.accessSpecifiers:
            t.type = t.value
        elif t.value in CppLexerClass.storageQualifiers:
            t.type = "STORAGE"
        elif t.value in CppLexerClass.functionQualifiers:
            t.type = t.value
        elif t.value in CppLexerClass.cvQualifiers:
            t.type = "CVQUAL"
        elif t.value in self._bareMacros:
            t.type = "BAREMACRO"
        elif t.value in self._macros:
            t.type = "MACROCALL"
            t.lexer.begin('macro')
        return t


    # Capture inline documentation
    def t_enum_BackDO2COMMENT(self,t):
        r'/\*\*\<(.|\n)*?\*/'
        t.lexer.lineno += t.value.count ('\n')
        t.type = 'UPDOC'
        return t

    def t_enum_BackDO2CPPCOMMENT(self,t):
        r'///\<[^\n]*\n'
        t.lexer.lineno += t.value.count ('\n')
        if t.lexer.lexstate == 'enum':
            t.type = 'UPDOC'        
            return t

    def t_ANY_DO2COMMENT(self,t):
        r'/\*\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count ('\n')
        t.type = 'DOC'
        return t

    def t_ANY_DO2CPPCOMMENT(self,t):
        r'///[^\n]*\n'
        t.lexer.lineno += t.value.count ('\n')
        if t.lexer.lexstate == 'enum':
            t.type = 'DOC'        
            return t
        
    # Comments
    def t_ANY_comment(self,t):
        r' /\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
            
    def t_ANY_ignore_cppcomment(self,t):
        r'//[^\n]*\n'
        t.lexer.lineno += t.value.count ('\n')

    # Preprocessor directive (ignored)
    # def t_preprocessor(t):
    #     r'\#(.)*?\n'
    #     if t.value.endswith ('\\\n'):
    #         data = t.lexer.lexdata  [t.lexer.lexpos]
    #         for i in range (t.lexer.lexpos, len (data)):
    #             if data [i] == '\n':
    #                 t.lineno += 1
    #             if data [i] == '\n' and data [i - 1] != '\\':
    #                 break
    #         t.lexer.lexpos = i + 1
    #     t.lineno += 1

    def t_ANY_error(self,t):
        print "Illegal character %s" % repr(t.value[0])
        t.lexer.skip(1)

tokens = CppLexerClass.tokens

def CppLexer():
    lexerClass = CppLexerClass()
    lexer = lex.lex(object=lexerClass)
    lexer.lexmodule = lexerClass
    return lexer

