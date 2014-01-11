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
import ply.yacc as yacc

# Operators (+,-,*,/,%,|,&,~,^,<<,>>, ||, &&, !, <, <=, >, >=, ==, !=)
operators = ('PLUS', 'MINUS', 'SLASH', 'PERCENT', 'VBAR', 'CARET', #'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'BANG', 'LE', 'GE', 'EQ', 'NE',
    # Increment/decrement (++,--)
    'PLUSPLUS', 'MINUSMINUS',
    # Assignment (=, *=, /=, %=, +=, -=, <<=, >>=, &=, ^=, |=)
    'TIMESEQUAL', 'DIVEQUAL', 'MODEQUAL', 'PLUSEQUAL', 'MINUSEQUAL',
    'LSHIFTEQUAL',#'RSHIFTEQUAL', 
    'ANDEQUAL', 'XOREQUAL', 'OREQUAL','EQUALS', 'ASTERISK', 'AMPERSAND', 'TILDE', 'LT', 'GT'
)

tokens = operators + (
# Literals (identifier, integer constant, float constant, string constant, char const)
'ID', 'ICONST', 'OCTCONST', 'HEXCONST', 'FCONST', 'SCONST', 'CCONST',

# Delimeters ( ) [ ] { } , . ; : ::
'LPAREN', 'RPAREN',
'LBRACKET', 'RBRACKET',
'LBRACE', 'RBRACE',
'COMMA', 'PERIOD', 'SEMI', 'COLON', 'COLON2',

'ARRAYOP', 'FUNCPTR', 'defined' 
)
    
# Completely ignored characters
t_ANY_ignore           = ' \t\x0c'

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

# Delimeters
t_LPAREN           = r'\('
t_RPAREN           = r'\)'
t_LBRACKET         = r'\['
t_RBRACKET         = r'\]'
t_LBRACE           = r'\{'
t_RBRACE           = r'\}'
t_COMMA            = r','
t_PERIOD           = r'\.'
t_SEMI             = r';'
t_COLON            = r':'
t_COLON2           = r'::'

# Hex Literal
def t_HEXCONST (t):
    r'0[x|X][\da-fA-F]+'
    t.value = eval (t.value)
    return t

# Octal Literal
t_OCTCONST = r'0[0-7]{3}?'

# Floating literal
def t_FCONST (t):
    r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'
    t.value = float (t.value)
    return t

# Integer literal
def t_ICONST (t):
    r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'
    t.value = int (t.value)
    return t

# Array operator
t_ARRAYOP = r'[[].*[]]'

# Function pointer
t_FUNCPTR = r'\(\s*\*'

# String literal
t_SCONST = r'\"([^\\\n]|(\\.))*?\"'

# Character constant 'c' or L'c'
t_CCONST = r'(L)?\'([^\\\n]|(\\.))*?\''
# Newlines

# def t_CONTINUATION (t):
#     r'\\\n'
#     t.lexer.lineno += t.value.count("\n")

def t_ANY_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
        

def t_ID(t):
    r'[A-Za-z_][\w_]*'
    if t.value == 'defined':
        t.type = 'defined'
    return t


# Comments
def t_ANY_comment(t):
    r' /\*(.|\n)*?\*/'
    t.lineno += t.value.count('\n')
        
t_ANY_ignore_cppcomment = '//[^/].*'
    
    
def t_ANY_error(t):
    print("Illegal character %s" % repr(t.value[0]))
    t.lexer.skip(1)

    
exprLexer = lex.lex ()

class ExpressionParser(object):
    precedence = (('left','PLUS','MINUS'), ('left','ASTERISK','SLASH'), ('right','UMINUS'), )
    
    def __init__ (self):
        self.lexer      = exprLexer
        self.test       = []       
        self.tokens = tokens        
        yacc.yacc (module = self, tabmodule = "expressionParserTab")
        self._parse = yacc.parse
                   
        self.values = {}                   
        
    def parse (self, s, mode = 'calc', values = None):
        self.values = values
        self.lexer.input (s)
        self.mode = mode
        self.result = None
        self._parse (debug = 0, lexer = self.lexer)
        return self.result

    def p_expression_result (self, p):
        'expression_result : expression'
        p [0] = p [1]
        self.result = p [0]

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
                     | HEXCONST"""                    
        p [0] = p [1]
            
    def p_expression1 (self, p):
        'expression : LPAREN expression RPAREN'
        p [0] = p [2]

    def p_expression2 (self, p):
        'expression : ID'
        if self.mode == 'calc':
            p [0] = self.values [p [1]]
        elif self.mode == 'def':
            p [0] = p [1] in self.values
    
    def p_unary_expression (self, p):
        """unary_expression : sign_expression
                           | not_expression
                           | bitnot_expression
                           | defined_expression"""
        p [0] = p [1]

    def p_add_expression (self, p):
        'add_expression : expression PLUS expression'
        p [0] = p [1] + p [3]
        
    def p_sub_expression (self, p):
        'sub_expression : expression MINUS expression'
        p [0] = p [1] - p [3]
    
    def p_mult_expression (self, p):
        'mult_expression : expression ASTERISK expression'
        p [0] = p [1] * p [3]
    
    def p_div_expression (self, p):
        'div_expression : expression SLASH expression'
        p [0] = p [1] / p [3]
    
    def p_mod_expression (self, p):
        'mod_expression : expression PERCENT expression'
        p [0] = p [1] % p [3]
    
    def p_sign_expression (self, p):
        'sign_expression : MINUS expression %prec UMINUS'
        p [0] = - p [2]
    
    def p_or_expression (self, p):
        'or_expression : expression LOR expression'
        p [0] = p [1] or  p [3]
    
    def p_and_expression (self, p):
        'and_expression : expression LAND expression'
        p [0] = p [1] and p [3]
    
    def p_xor_expression (self, p):
        'xor_expression : expression CARET expression'
        p [0] = p [1] ^ p [3]
    
    def p_bitor_expression (self, p):
        'bitor_expression : expression VBAR expression'
        p [0] = p [1] | p [3]
    
    def p_bitand_expression (self, p):
        'bitand_expression : expression AMPERSAND expression'
        p [0] = p [1] & p [3]
    
    def p_lt_expression (self, p):
        'lt_expression : expression LT expression'
        p [0] = p [1] < p [3]
    
    def p_le_expression (self, p):
        'le_expression : expression LE expression'
        p [0] = p [1] <= p [3]
    
    def p_eq_expression (self, p):
        'eq_expression : expression EQ expression'
        p [0] = p [1] == p [3]
    
    def p_ge_expression (self, p):
        'ge_expression : expression GE expression'
        p [0] = p [1] >= p [3]
    
    def p_gt_expression (self, p):
        'gt_expression : expression GT expression'
        p [0] = p [1] > p [3]
    
    def p_lshift_expression (self, p):
        'lshift_expression : expression GT GT expression'
        p [0] = p [1] >> p [4]
    
    def p_rshift_expression (self, p):
        'rshift_expression : expression LT LT expression'
        p [0] = p [1] << p [4]

    def p_not_expression (self, p):
        'not_expression : BANG expression'
        p [0] = not p [2]

    def p_bitnot_expression (self, p):
        'bitnot_expression : TILDE expression'
        p [0] = ~ p[2]

    def p_defined_expression0 (self, p):
        'defined_expression : defined ID'
        p [0] = p[2] in self.values

    def p_defined_expression1 (self, p):        
        'defined_expression : defined LPAREN ID RPAREN'
        p [0] = p[3] in self.values
    
    def p_error(self, p):
        print("Syntax error at '%s'" % p.value)

                  
if __name__ == '__main__':                  
    text = '2 +\
     2'
    
    parser = ExpressionParser ()
#    exprLexer.input (text)
#    print parser.parse (text, None)
    values = {'x': 2.0, 'macro': None}
    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s: continue
        print(parser.parse(s, values))
