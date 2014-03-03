# -*- coding: utf-8 -*-
#     Copyright 2014 Simon Edwards <simon@simonzone.com>
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

import cmakelexer
import ply.yacc as yacc

class CMakeThing(object):
    def isString(self):
        return False
    def isSymbol(self):
        return False
    def value(self):
        return self._value

class CMakeString(CMakeThing):
    def __init__(self, value):
        self._value = value
    def isString(self):
        return True
    def __eq__(self, other):
        return isinstance(other, CMakeString) and other._value == self._value
    def __repr__(self):
        return 'CMakeString("{0}")'.format(self._value)

class CMakeSymbol(CMakeThing):
    def __init__(self, value):
        self._value = value
    def isSymbol(self):
        return True
    def __eq__(self, other):
        return isinstance(other, CMakeSymbol) and other._value == self._value
    def __repr__(self):
        return 'CMakeSymbol("{0}")'.format(self._value)

class CMakeCommand(object):
    def __init__(self, command, arguments):
        self._command = command
        self._arguments = arguments
    def command(self):
        return self._command
    def arguments(self):
        return self._arguments
    def __eq__(self, other):
        return isinstance(other, CMakeCommand) and other._command == self._command and \
            other._arguments == self._arguments
    def __repr__(self):
        return "CMakeCommand({0}, {1})".format(self._command, repr(self._arguments))

class CMakeParser(object):

    def __init__(self):
        self.tokens = cmakelexer.tokens
        yacc.yacc (module = self, tabmodule = "cmakeParserTab")
        self._parse = yacc.parse

        self.values = {}

    def parse(self, s, filename=None):
        self.lexer = cmakelexer.CMakeLexer(filename)
        self.lexer.input(s)
        self.result = None
        self.filename = filename
        self._parse(debug = 0, lexer = self.lexer)
        return self.result

    def p_cmake_file(self, p):
        """cmake_file : statement_list"""
        p[0] = p[1]
        self.result = p[0]

    def p_statement_list1(self, p):
        """statement_list : statement"""
        if p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_statement_list2(self, p):
        """statement_list : statement_list statement"""
        if p[2] is not None:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = p[1]

    def p_statement1(self, p):
        """statement : SYMBOL LPAREN argument_list RPAREN"""
        p[0] = CMakeCommand(p[1], p[3])

    def p_statement2(self, p):
        """statement : COMMENT"""
        p[0] = None

    def p_statement3(self, p):
        """statement : SYMBOL LPAREN RPAREN"""
        p[0] = CMakeCommand(p[1], [])

    def p_argument_list(self, p):
        """argument_list : argument
                         | argument_list argument"""
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] + p[2]

    def p_argument1(self, p):
        """argument : SYMBOL"""
        p[0] = [CMakeSymbol(p[1])]

    def p_argument2(self, p):
        """argument : STRING"""
        p[0] = [CMakeString(p[1])]

    def p_argument3(self, p):
        """argument : COMMENT"""
        p[0] = []

    def p_argument4(self, p):
        """argument : LPAREN argument_list RPAREN"""
        p[0] = [CMakeSymbol("(")] + p[2] + [CMakeSymbol(")")]

    def p_error(self, p):
        if self.filename is None:
            print("Syntax error at line %d, '%s'" % (self.lexer.lineno, p.value,))
        else:
            print("Syntax error at line %d, '%s' in file %s" % (self.lexer.lineno, p.value, self.filename))
