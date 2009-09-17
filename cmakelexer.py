# -*- coding: utf-8 -*-
import ply.lex as lex

class CMakeLexerClass(object):
    states = ( ('command', 'exclusive'), ('arguments', 'exclusive') )

    tokens = (
       'COMMAND',
       'ARGUMENT'
    )

    t_ANY_ignore = " \t"

    def t_COMMAND(self,t):
        r'[A-Za-z0-9_]+'
        t.lexer.last_command = t.value
        t.lexer.begin('command')

    def t_command_LPAREN(self,t):
        r'\('
        t.type = 'COMMAND'
        t.lexer.begin('arguments')
        t.value = t.lexer.last_command
        return t
        
    def t_ANY_comment(self,t):
        r'\#.*'
        pass
    
    def t_arguments_RPAREN(self,t):
        r'\)'
        #if parenStack.pop ():
        #t.type = 'COMMAND_END'
        t.lexer.begin('INITIAL')
        #else:
        #    t.type = 'RPAREN'
        #return t
        
    t_arguments_ARGUMENT = '[^" \t\n)]+|("((\\\\")|(\\\\n)|[^\\\\"]|\\.)*?")'
        #("([^\n]|(\.))*?")'

    # Define a rule so we can track line numbers
    def t_ANY_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self,t):
        print("Line %i: Illegal character %s" % (t.lexer.lineno,repr(t.value[0])))
        t.lexer.skip(1)

classinstance = CMakeLexerClass()

def CMakeLexer():
    return lex.lex(object=classinstance)
