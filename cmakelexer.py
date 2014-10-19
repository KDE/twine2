# -*- coding: utf-8 -*-
import ply.lex as lex

tokens = (
   'SYMBOL',
   'LPAREN',
   'RPAREN',
   'COMMENT',
   'STRING'
)

class CMakeLexerClass(object):
    def __init__(self, filename=None):
        self._filename = filename

    # states = ( ('command', 'exclusive'), ('arguments', 'exclusive') )

    tokens = tokens

    t_ANY_ignore = " \t"
    def t_SYMBOL(self, t):
        r'[^\\()\s#"]+(\\"[^()\s#"\\]*)*'
        t.value = t.value.replace(r'\"', '"')
        return t

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_ANY_COMMENT = r'\#.*'

    def t_STRING(self, t):
        r'"[^"\\]*(\\"[^"\\]*)*"'
        t.value  = t.value[1:-1].replace(r'\"', '"')
        t.lexer.lineno += t.value.count("\n")
        return t

    # Define a rule so we can track line numbers
    def t_ANY_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self,t):
        if self._filename is not None:
            print("Illegal character %s at line %i, %s" % (repr(t.value[0]), t.lexer.lineno, self._filename))
        else:
            print("Illegal character %s at line %i." % (repr(t.value[0]),t.lexer.lineno))
        t.lexer.skip(1)

def CMakeLexer(filename=None):
    return lex.lex(object=CMakeLexerClass(filename))
