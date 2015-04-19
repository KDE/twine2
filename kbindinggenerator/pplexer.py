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

import re
import ply.lex as lex
# handles the evaluation of conditionals
from exprparser import ExpressionParser

newtext   = []
macros    = []
bitBucket = False
sentinel  = False

preprocessor_tokens =  ['cond', 'else', 'endif', 'include', 'define', 'undef', 'line', 'error', 'pragma', 'warning']
tokens = preprocessor_tokens + ['anyline']

values = {}
evaluate = ExpressionParser ().parse

# Completely ignored characters
t_ANY_ignore           = ' \t\x0c'

def stripComment (s):
    pos1 = s.find ('\/\*')
    pos2 = s.find ('\/\/')
    if pos1 > 0 and pos2 > 0:
        pos = min (pos1, pos2)
    elif pos1 < 0 and pos2 < 0:
        pos = -1
    else:
        pos = max (pos1, pos2)
    
    if pos > 0:
        return s [:pos].strip (), s[pos:].strip ()
    else:
        return s, ''

def t_cond (t):
    r'\#\s*(?P<ifType>ifdef\s|ifndef\s|if\s|elif\s)\s*(?P<cond>.*?)\n'

    # All conditionals that perform a test are handled here
    global newtext
    ifType = t.lexer.lexmatch.group ('ifType').strip ()
    condition, comment  = stripComment (t.lexer.lexmatch.group ('cond'))
    
    # #if/#elif look for True/False, others for defintion only
    # #if defined - 'defined' is handled as an operator by the
    # expression parser which evaluates the conditional
    if ifType in ['if', 'elif']:
        mode = 'calc'
    else:
        mode = 'def'

    ifCondition = evaluate (condition, mode, values)
        
    global bitBucket, sentinel
    bitBucket = ((not ifCondition) and (ifType != 'ifndef')) or (ifCondition and (ifType == 'ifndef'))
    
    # remove #define <sentinel>?
    sentinel = not bitBucket and ('_h' in condition or '_H' in condition)

    # A multiline comment could begin on a preprocessor line
    # that's being eliminated here
    if bitBucket and comment:
        newtext.append (comment + '\n')
    else:
        newtext.append ('\n')

    t.lexer.lineno += 1
    
def t_else (t):
    r'\#\s*else(.*?)\n'  # comments?
    global bitBucket, newtext
    bitBucket = not bitBucket
    t.lexer.lineno += 1
    newtext.append ('\n')
    
def t_endif (t):
    r'\#\s*endif(.*?)\n'
    global bitBucket, newtext
    bitBucket = False
    t.lexer.lineno += 1
    newtext.append ('\n')

def t_include (t):
    r'\#\s*include.*?\n'
    global newtext
    t.lexer.lineno += 1
    newtext.append ('\n')
    
def t_line (t):
    r'\#\s*line.*?\n'
    global newtext
    t.lexer.lineno += 1
    newtext.append ('\n')

def t_error (t):    
    r'\#\s*error.*?\n'
    global newtext
    t.lexer.lineno += 1
    newtext.append ('\n')
    
def t_pragma (t):    
    r'\#\s*pragma.*?\n'
    global newtext
    t.lexer.lineno += 1
    newtext.append ('\n')
    
def t_warning (t):    
    r'\#\s*warning.*?\n'
    global newtext
    t.lexer.lineno += 1
    newtext.append ('\n')

def t_undef (t):
    r'\#\s*undef\s*(?P<item>.*?)\n'
    global macros, values, newtext
    item = t.lexer.lexmatch.group ('item').strip ()
    if item in values:
        macros = [macro for macro in macros if len(macro)==2 or macro[2] != item]
        del values [item]
    t.lexer.lineno += 1
    newtext.append ('\n')
    
def t_define (t):
    r'\#\s*define\s*(?P<first>[\S]+)\s*?(?P<second>[^\n]*?)\n'    
    global sentinel, values, macros, newtext
    a = t.lexer.lexmatch.group ('first')
    b = t.lexer.lexmatch.group ('second')
    
    # Append any continuation lines
    newlines = 1
    start = t.lexer.lexpos
    if b and b.endswith ('\\'):              
        data = t.lexer.lexdata
        for i in range (start, len (data)):
            if data [i] == '\n':
                t.lexer.lineno += 1
                newlines += 1
            if data [i] == '\n' and data [i - 1] != '\\':                
                break
        t.lexer.lexpos = i + 1
        b += data [start:t.lexer.lexpos].replace ('\\\n', ' ')

    if '(' in a and not ')' in a:
        pos = b.find (')')
        if pos < 0:
            return
        a += b [:pos + 1]
        b = b [pos + 1:]
    
    # remove #define <sentinel>
    sentinel = sentinel and not b and ('_h' in a or '_H' in a)
    if not sentinel:
        if not b or '(' in a:
            values [a] = ''
            macros.insert (0, (re.compile (a), '', a))
        else:
            values [a] = b
            macros.insert (0, (re.compile (a), b.strip (), a))
    
    sentinel = False
            
    newtext.append (newlines *'\n')
    t.lexer.lineno += 1
    
def t_anyline (t):
    r'[^\n]*?\n(([^#\n][^\n]*\n)|\n)*'
    """
    Process anything that's not a preprocesor directive.

    Apply all #define macros to each line. Code that has
    been #if'd out (bitBucket == True) is replaced by
    a single newline for each line removed.
    """
    global sentinel, newtext
    sentinel = False
    if not bitBucket:
        line = t.value
        for m in macros:
            line = m[0].sub(m[1], line)
        newtext.append (line)
        t.lexer.lineno += line.count('\n')
    else:
        c = t.value.count('\n')
        for x in range(c):
            newtext.append('\n')
        t.lexer.lineno += c

# this needs to be HERE - not above token definitions
ppLexer = lex.lex (debug=0)

    
def preprocess (text, global_values={}, global_macros=[]):
    """
    Preprocess a C/C++ header file text
    
    Preprocesses h files - does #define substitutions and
    evaluates conditionals to include/exclude code. No
    substitutions are performed on preprocessor lines (any
    line beginning with '#'). Global #defines are applied
    LAST, so they override any local #defines.

    All C preprocessor code is stripped, and along with any
    lines eliminated conditionally, is replaced with newlines
    so that error messages still refer to the correct line in
    the original file.
    
    Arguments:
    text -- The text to process.
    global_values -- Dict mapping string variable names to values.
    global_macros -- List of tuples. The first value in a tuple is a
                     regular expression object. The second is that
                     replacement string which may contain re module
                     back references.
    
    Returns the processed string.
    """
    global newtext, bitBucket, macros, values
    newtext   = []
    bitBucket = False
    macros    = [] + global_macros
    values    = {}
        
    values.update (global_values)
    if text[-1]!='\n':
        text = text + '\n'
    ppLexer.input (text)
    token = ppLexer.token()
    #print(newtext)
    #return "".join (fixDoc (newtext))
    return "".join(newtext)

def fixDoc (textList):
    doReplace = False
    doBackReplace = False
    nLines    = len (textList)
    for i in range (nLines):
        if i >= nLines - 1:
            break
            
        if textList [i].startswith ('/////'):
            textList [i] = '\n'
            continue
            
        haveBackCmt = textList [i].find ('///<') >= 0
        haveCmt = textList [i].find ('///') >= 0 and not haveBackCmt
        if haveBackCmt:
            if not doBackReplace:
                doBackReplace = textList [i + 1].strip ().startswith ('///<')
                if doBackReplace:
                    textList [i] = textList [i].replace ('///<', '/**<')
            else:
                textList [i] = textList [i].replace ('///<', '*')            
        elif doBackReplace:
            textList.insert (i, '*/\n')
            doBackReplace = False
            
        if not haveBackCmt and haveCmt:
            if not doReplace:
                doReplace = textList [i + 1].strip ().startswith ('///')
                if doReplace:
                    textList [i] = textList [i].replace ('///', '/**')
            else:
                textList [i] = textList [i].replace ('///', '*')
        elif doReplace:
            textList.insert (i, '*/\n')
            doReplace = False
            
    return textList
    
if __name__ == '__main__':
    text = """#define foo bar"""
