# -*- coding: utf-8 -*-
#     Copyright 2007-8 Jim Bublitz <jbublitz@nwinternet.com>
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
import string

states = (('enum', 'inclusive'), ('function', 'inclusive'), ('variable', 'inclusive'),\
          ('block', 'exclusive'), ('sipStmt', 'exclusive'), ('filename', 'exclusive'), \
          ('string', 'exclusive'), ('dottedname', 'exclusive'), ('keypairs','exclusive'), \
          ('keypairs2','exclusive'))

blockTokens = ('AccessCode', 'BIGetCharBufferCode', 'BIGetReadBufferCode', 'BIGetSegCountCode',\
               'BIGetWriteBufferCode', 'ConvertToSubClassCode', 'ConvertToTypeCode',\
               'ConvertFromTypeCode', 'Copying', 'Doc', 'ExportedDoc', 'ExportedHeaderCode',\
               'FinalisationCode', 'GCClearCode', 'GCTraverseCode', 'GetCode', 'MethodCode', 'ModuleCode',\
               'ModuleHeaderCode', 'PickleCode', 'PostInitialisationCode', 'PreInitialisationCode',\
               'RaiseCode', 'SetCode', 'TypeCode', 'TypeHeaderCode', 'UnitCode', 'VirtualCatcherCode',\
               'Makefile', 'PrePythonCode',\
               'BIGetBufferCode','BIGetCharBufferCode','BIGetReadBufferCode','BIGetSegCountCode',\
               'BIGetWriteBufferCode','BIReleaseBufferCode', 'InitialisationCode','Docstring')

argumentAnnotations = ('AllowNone', 'Array', 'ArraySize', 'Constrained', 'In', 'Out', 'TransferThis',\
                       'GetWrapper')
                      
               
classAnnotations = ('Abstract', 'DelayDtor', 'External', 'NoDefaultCtors')

functionAnnotations = ('Default', 'Factory', 'HoldGIL', 'NewThread', 'NoDerived',\
                       'Numeric', 'ReleaseGIL')

valueAnnotations = ('PyName', 'PostHook', 'PreHook', 'AutoGen', 'TypeFlags', 'Encoding')

multipleAnnotations = ('Transfer', 'TransferBack')
               
stmtTokens = ('Exception', 'MappedType')

sipDirectives = ('CModule', 'CompositeModule', 'ConsolidatedModule', 'End', 'Feature', 'If',\
                 'Import', 'Include', 'License', 'Module', 'OptionalInclude', 'Platforms',\
                 'SIPOptions', 'Timeline', 'Plugin', 'DefaultEncoding', 'DefaultMetatype',\
                 'DefaultSupertype','API')

accessSpecifiers = ("private", "protected", "public", "slots", "signals")

edges = ("class", "struct", "union",  "template", "enum", "namespace",\
         "typedef",  "operator")
         
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
    'ANDEQUAL', 'XOREQUAL', 'OREQUAL'
)

cppTokens = edges + cppScalarTypes + functionQualifiers + operators + accessSpecifiers

tokens = cppTokens + sipDirectives + (
# Literals (identifier, integer constant, float constant, string constant, char const)
'ID', 'ICONST', 'HEXCONST', 'FCONST', 'SCONST', 'CCONST', 'CVQUAL', 
'STORAGE', #'PURESFX',

# Expressions we don't parse
#'ENUMINIT',
'ARRAYOP', 'FUNCPTR', 'BLOCK_BODY', 'BLOCK', 'SIPSTMT', 
'SIPSTMT_BODY', 'FILENAME', 'licenseAnnotation', 'IG', 'throw',
'FORCE', 'END', 'STRING', 'DOTTEDNAME', 'LINECOMMENT', 'CCOMMENT', 'BLANKLINE',

# Structure dereference (->)
'ARROW',

# Treat separately from other operators
'EQUALS', 'ASTERISK', 'AMPERSAND', 'TILDE', 'LT', 'GT',
# Conditional operator (?)
#'CONDOP',

# Delimeters ( ) [ ] { } , . ; : ::
'LPAREN', 'RPAREN',
'LBRACKET', 'RBRACKET',
'LBRACE', 'RBRACE',
'COMMA', #'PERIOD', 
'SEMI', 'COLON', 'COLON2',

# Ellipsis (...)
'ELLIPSIS'
)

# Completely ignored characters
t_ANY_ignore           = ' \t\x0c'
t_block_ignore         = ''

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

# ?
#t_CONDOP           = r'\?'

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
#t_PERIOD           = r'\.'
t_SEMI             = r';'
t_COLON            = r':'
t_ELLIPSIS         = r'\.\.\.'
t_COLON2           = r'::'

# Hex Literal
t_HEXCONST = r'0[x|X][\da-fA-F]+'

# Octal Literal
#t_OCTCONST = r'0[0-7]{3}?'

# Integer literal
t_ICONST = r'(0(?![x|X])|[1-9])\d*([uU]|[lL]|[uU][lL]|[lL][uU])?'

# Floating literal
t_FCONST = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

# Enumerator initializer
#t_enum_ENUMINIT = r'[^,}=]*(?=[,}])+'

# Array operator
t_ARRAYOP = r'[[][^(]*?[]]'

# Function pointer
t_FUNCPTR = r'\(\s*\*'

# String literal
t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c' or L'c'
t_CCONST = r'(L)?\'([^\\\n]|(\\.))*?\''
# Newlines

t_licenseAnnotation = r'(Licensee|Signature|Timestamp|Type)\s*=\s*"\w*?"(?=,|\/)'
def t_ANY_IG (t):
    '\/\/ig.?'
    t.type = 'IG'
    return t
    
def t_ANY_FORCE (t):
    '\/\/force'
    t.type = 'FORCE'
    return t

def t_ANY_END (t):
    '\/\/end'
    t.type = 'END'
    return t

    # some things we ignore (entire line)
def t_friend_class (t):
    r'friend\s+class\s+[^;]*;?'
    t.lexer.lineno += t.value.count("\n")

def t_friend (t):
    r'friend\s'
    pass    

def t_using (t):
    r'using\s+.*;?'
    t.lexer.lineno += t.value.count ('\n')

def t_inline (t):
    r'inline\s+'
    pass

# any sip block - %<blocktype> ... %End
# This has high prio than t_ANY_NEWLINE
def t_block_BLOCK_BODY (t):
    r'(.|\n)*?%End'
    t.lexer.lineno += t.value.count("\n")
    t.lexer.begin ('variable')
    return t

def t_ANY_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1
    pos = t.lexpos-1
    while True:
        if (pos < 0) or (t.lexer.lexdata[pos]=='\n'):
            t.value = t.lexer.lexdata[pos+1:t.lexpos+1]
            t.type = 'BLANKLINE'
            return t
        elif t.lexer.lexdata[pos] not in string.whitespace:
            break
        pos -= 1
        
def t_sipStmt_SIPSTMT_BODY (t):
    r'(?s){.*?\n};'
    t.lexer.lineno += t.value.count("\n")
    t.lexer.begin ('variable')
    return t

def t_sipStmt_ID (t):
    r'[A-Za-z_][\w_]*'
    if t.value in cvQualifiers:
        t.type = "CVQUAL"
    return t

def t_sipStmt_String(t):
    r'"[^"]*"'
    t.type = "SCONST"
    return t

t_sipStmt_SLASH    = r'\/'
t_sipStmt_LT       = r'<'
t_sipStmt_GT       = r'>'
t_sipStmt_COLON2   = r'::'
t_sipStmt_ASTERISK = r'\*'
t_sipStmt_COMMA    = r','
t_sipStmt_EQUALS   = r'='
t_sipStmt_COLON    = r':'
t_sipStmt_MINUS    = r'-'
t_sipStmt_ICONST   = t_ICONST

def t_filename_FILENAME (t):
    r'[._A-Za-z][._/A-Za-z0-9\-]*[._A-Za-z0-9]'
    t.lexer.begin ('variable')
    return t

def t_keypairs_FILENAME (t):
    r'[._A-Za-z][._/A-Za-z0-9\-]*[._A-Za-z0-9]'
    t.lexer.begin ('variable')
    return t
    
def t_keypairs_LPAREN(t):
    r'\('
    t.lexer.begin('keypairs2')
    return t
    
t_keypairs2_FILENAME = r'[._/A-Za-z0-9\-]+'
t_keypairs2_STRING = r'"[^"]*"'
def t_keypairs2_RPAREN(t):
    r'\)'
    t.lexer.begin ('variable')
    return t

t_keypairs2_EQUALS = r'='
t_keypairs2_COMMA = r','
    
def t_string_STRING (t):
    r'"[^"]*"'
    t.lexer.begin ('variable')
    return t

def t_dottedname_DOTTEDNAME (t):
    r'([A-Za-z_][A-Za-z0-9_]*\.?)+'
    t.lexer.begin ('variable')
    return t

def t_SIP_SLOT_CON (t):
    r'SIP_SLOT_CON\s*\(.*?\)'
    t.type = 'ID'
    return t

def t_SIP_SLOT_DIS (t):
    r'SIP_SLOT_DIS\s*\(.*?\)'
    t.type = 'ID'
    return t

def t_ID(t):
    r'[A-Za-z_][\w_.]*'
    if t.value in edges:
        t.type = t.value
    elif t.value in cppScalarTypes:
        t.type = t.value
    elif t.value in accessSpecifiers:
        t.type = t.value
    elif t.value in storageQualifiers:
        t.type = "STORAGE"
    elif t.value in functionQualifiers:
        t.type = t.value
        if t.value == 'virtual' and stateInfo:
            stateInfo.virtual = True
    elif t.value in cvQualifiers:
        t.type = "CVQUAL"
    elif t.value in blockTokens:
        t.type = 'BLOCK'
        t.lexer.begin ('block')
    elif t.value in stmtTokens:
        pos = t.lexer.lexpos - len (t.value) - 1
        if t.lexer.lexdata [pos] == '%':
            t.type = 'SIPSTMT'
            t.lexer.begin ('sipStmt')        
    elif t.value in sipDirectives:
        pos = t.lexer.lexpos - len (t.value) - 1
        if t.lexer.lexdata [pos] == '%':
            if t.value in ['Import', 'OptionalInclude']:
                t.lexer.begin('filename')
            elif t.value in ['Module','API', 'Include']:
                t.lexer.begin('keypairs')
            elif t.value=='DefaultEncoding':
                t.lexer.begin('string')
            elif t.value in ['DefaultMetatype','DefaultSupertype']:
                t.lexer.begin('dottedname')
            t.type = t.value
    elif t.value == 'throw':
        t.type = t.value
    return t

# Capture inline documentation
def t_ANY_DO2COMMENT (t):
    r'/\*\*(.|\n)*?\*/'
    if stateInfo:
        stateInfo.setDoc (t.value)
    t.lexer.lineno += t.value.count ('\n')

def t_ANY_DO2CPPCOMMENT (t):
    r'///.*'
    if stateInfo:
        stateInfo.setDoc (t.value)

# Comments
def t_ANY_comment(t):
    r'/\*[^\*](.|\n)*?\*/'
    t.lineno += t.value.count('\n')
    t.type = 'CCOMMENT'
    return t

def t_ANY_cppcomment (t):
    r'//[^\n]*\n'
    t.lexer.lineno += t.value.count ('\n')
    t.type = 'LINECOMMENT'
    return t
    
# Preprocessor directive (ignored)
def t_preprocessor(t):
    r'\#(.)*?\n'
    t.lineno += 1

def t_ANY_error(t):
    print "Illegal character %s" % repr(t.value[0])
    t.lexer.skip(1)


sipLexer = lex.lex ()

# for collecting inline docs
stateInfo = None

def setStateInfoTarget (si):
    global stateInfo
    stateInfo = si
