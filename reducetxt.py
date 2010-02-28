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

from string import lowercase
import re

deleteWords = ["@attention", "@exception", "@name", "\\name", "@e", "@port4", "@private", "@reimp",\
    "@{", "@}", "@class", "@copydoc", "@bc", "@file", "\\file", "@overload", "\\overload",\
    "\\e", "@brief", "\\brief", "\\brief", "\\short", "@short", "@c", "\\c", "@ref",\
    "\\ref",  "@enum", "\\par", "\\link", "\\endlink", "\\}", "\\n"]

deleteLine  = ["@defgroup", "@namespace", "\\relates", "\\subsection", "@ingroup", \
    "\\ingroup","\\namespace","\\headerfile"]

replaceWord = {
    "@todo": "To do:",
    "\\todo": "To do:",
    "@flags": "<b>flags</b> - ",
    "@version": "<b>Version:</b>",
    "@url": "<b>url</b>",
    "(\b": "(",
    "\\verbatim": "<pre>",
    "\\endverbatim": "</pre>",
    r'%KDE': "KDE",
    r'%Solid': "Solid"
}
lgpllink = '<a href="http://www.gnu.org/licenses/old-licenses/lgpl-2.1.html#SEC1">LGPLv2</a>'
gpllink = '<a href="http://www.gnu.org/licenses/old-licenses/gpl-2.0.html#SEC1">GPLv2</a>'
rawReplaceWord = {
    "@lgpl": lgpllink,
    "\\lgpl": lgpllink,
    "@gpl": gpllink,
    "@lgpl<br>": lgpllink,
    "@gpl<br>": gpllink,
    "<code>": "<pre>",
    "</code>": "</pre>"
}                   
                
boldWordNL  =  ["@value", "@var", ]

boldWord    =  ["@a", "\\a", "@p", "\\p", "@b", "\\b", "@em"]

def escapeHtml(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def escapeDoyxgenHtml(s):
    es = escapeHtml(s.replace('\\<','<').replace('\\>','>'))
    es = es.replace('&lt;br&gt;','<br>')
    es = es.replace('&lt;p&gt;','<p>')
    es = es.replace('&lt;/p&gt;','</p>')
    es = es.replace('&lt;b&gt;','<b>')
    es = es.replace('&lt;/b&gt;','</b>')
    return es
    
ahref_re = re.compile("&lt;a href.*?&gt;",re.IGNORECASE)
def handleTags(x):
    i = 0
    m = ahref_re.search(x,i)
    parts = []
    while m:
        parts.append(x[i:m.start()])
        parts.append(m.group().replace('&lt;','<').replace('&gt;','>'))
        i = m.end()
        m = ahref_re.search(x,i)
    parts.append(x[i:])
    return (''.join(parts)).replace('&lt;/a&gt;','</a>')
    
class Reduce(object):
    def __init__ (self):
        pass

    def do_txt (self, txt):
        txt = txt.replace ('/**<', '')
        txt = txt.replace ('/**', '')
        txt = txt.replace ('*/', '')
        txt = txt.replace ('\n*', '\n')
        txt = txt.replace ('///<', '')
        txt = txt.replace ('///', '')
        return self.fixDoc (txt.strip ())
        
    def replace (self, word):
        if word in replaceWord:
            return replaceWord [word]
        else:
            return word
    
    def delete (self, line):
        for word in deleteLine:
            if word in line:
                return True
        return False            
    
    
    def fixDoc (self, txt):
        STATE_NORMAL = 0
        STATE_PARAM = 1
        STATE_PARAM_TRAILING = 2
        STATE_DL = 3
        STATE_CODE = 4
        STATE_LICENSES = 5
        STATE_NBULLET = 6
        STATE_NBULLET_TRAILING = 7
        STATE_SKIP = 8
        
        state = STATE_NORMAL

        txt = txt.replace ("::", ".")
        lines = txt.split ("\n")
        doclines = [line for line in lines if not self.delete (line)]

        for i in range (len (doclines)):
            if state==STATE_SKIP:
                break
            strippedline = doclines [i].strip ()
            
            parts = strippedline.split(" ")
            firstword = parts[0] if len(parts)!=0 else None
            
            newdocline = []
            if state==STATE_PARAM:
                if strippedline=="":
                    newdocline.append("</td></tr>")
                    state = STATE_PARAM_TRAILING
                elif firstword not in boldWord and firstword!="@param" and \
                        (firstword.startswith('@') or firstword.startswith('\\')):
                    newdocline.append("</td></tr>")
                    newdocline.append("</table></dl>\n<p>")
                    state = STATE_NORMAL
                    
            elif state==STATE_PARAM_TRAILING:
                if strippedline!="" and not firstword=="@param":
                    newdocline.append("</table></dl>\n<p>")
                    state = STATE_NORMAL
                    
            elif state==STATE_NBULLET:
                if strippedline=="":
                    newdocline.append("</li>")
                    state = STATE_NBULLET_TRAILING
                elif firstword not in boldWord and firstword!="-#" and \
                        (firstword.startswith('@') or firstword.startswith('\\')):
                    newdocline.append("</li></ol>")
                    newdocline.append("\n<p>")
                    state = STATE_NORMAL
                    
            elif state==STATE_NBULLET_TRAILING:
                if strippedline!="" and not firstword=="-#":
                    newdocline.append("</ol>\n<p>")
                    state = STATE_NORMAL
                                
            if state==STATE_DL:
                if strippedline=="" or firstword.startswith('@') or firstword.startswith('\\'):
                    newdocline.append("</dd></dl>")
                    state = STATE_NORMAL
            
            if state==STATE_LICENSES:
                if strippedline=="" or (firstword.startswith('@') and firstword!="@lgpl") or \
                        (firstword.startswith('\\') and firstword!="\\lgpl"):
                    newdocline.append("</dd></dl>")
                    state = STATE_NORMAL
            
            if state==STATE_CODE:
                if firstword=="\\endcode" or firstword=="@endcode":
                    newdocline.append("</pre>")
                    state = STATE_NORMAL
                else:
                    newdocline.append(escapeHtml(doclines[i]))
    
            elif i and not strippedline:
                if state==STATE_NORMAL:
                    newdocline.append("</p>\n<p>")
        
            else:
                rawline = strippedline.split(" ")
    
                # take care of "@ markup" cases and remove blanks
                line = []
                atFlag = False
                for word in rawline:
                    if word == "@":
                        atFlag = True
                    elif word != " ":
                        if atFlag:
                            line.append ("@%s" % word)
                            atFlag = False
                        elif word not in deleteWords:
                            line.append (word)
    
                line = [self.replace (word) for word in line]
                j = 0
                originallinelen = len(line)
                while j < originallinelen:
                    word = line [j]
                    
                    if word=='@author' or word=='\\author':
                        line [j] = '\n<dl class="author" compact><dt><b>Author:</b></dt><dd>'
                        line.append("</dd></dl>")
                        
                    elif word=='@authors' or word=='\\authors':
                        line [j] = '\n<dl compact><dt><b>Author(s):</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@maintainers' or word=='\\maintainers':
                        line [j] = '\n<dl compact><dt><b>Maintainer(s):</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@licenses' or word=='\\licenses':
                        line [j] = '\n<dl compact><dt><b>License(s):</b></dt><dd>'
                        state = STATE_LICENSES
                        
                    elif word=='@return' or word=='\\return' or word=='@returns' or word=='\\returns':
                        line [j] = '<dl class="return" compact><dt><b>Returns:</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@see' or word=='\\see':
                        line [j] = '<dl class="see" compact><dt><b>See also:</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@since' or word=='\\since':
                        line [j] = '<dl class="since" compact><dt><b>Since:</b></dt><dd>'
                        state = STATE_DL
                    
                    elif word=='@note' or word=='\\note':
                        line [j] = '<dl class="note" compact><dt><b>Note:</b></dt><dd>'
                        state = STATE_DL
                    
                    elif word=='@internal' or word=='\\internal':
                        line [j] = '<dl class="internal" compact><dt><b>Internal:</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@deprecated' or word=='\\deprecated':
                        line [j] = '<dl class="deprecated" compact><dt><b>Deprecated:</b></dt><dd>'
                        state = STATE_DL
                    
                    elif word=='@obsolete' or word=='\\obsolete':
                        line [j] = '<dl class="obsolete" compact><dt><b>Obsolete:</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@warning' or word=='\\warning':
                        line [j] = '<dl class="warning" compact><dt><b>Warning:</b></dt><dd>'
                        state = STATE_DL
                        
                    elif word=='@code' or word=='\\code':
                        line[j] = '<pre class="fragment">'
                        state = STATE_CODE                    

                    elif word in rawReplaceWord:
                        line[j] = rawReplaceWord[word]
                        
                    elif word=="-#":
                        if state==STATE_NORMAL:
                            openList = '</p><ol type="1">'
                        else:
                            openList = ""
                        
                        line [j] = openList + '<li>'
                        state = STATE_NBULLET
                        
                    elif word=="\\page":    # Cut the dox off at this point.
                        line[j] = ''
                        line = line[0:j+1]
                        doclines = doclines[0:i+1]
                        state = STATE_SKIP
                        break
                    
                    elif j < len(line)-1:
                    
                        nextWord = line [j + 1]
                        if word in boldWord:
                            line [j] = ""
                            line [j + 1] = "<b>%s</b>" % escapeHtml(nextWord)
                            j += 1
                            
                        elif word=="@param" or word=="\\param":
                            line [j] = ""
                            if state==STATE_NORMAL:
                                openTable = '</p><dl compact><dt><b>Parameters:</b></dt><dd>\n<table border="0" cellspacing="2" cellpadding="0">'
                            else:
                                openTable = ""
                            
                            line [j + 1] = openTable + '\n<tr><td></td><td valign="top"><em>%s</em>&nbsp;</td><td>' % nextWord
                            j += 1
                            state = STATE_PARAM
                            
                        elif word in boldWordNL:
                            line [j] = ""
                            line [j + 1] = "\n<b>%s</b> -" % escapeHtml(nextWord)
                            j += 1
                            
                        elif word=="@mainpage" or word=="\\mainpage":
                            line [j] = ""
                            line [j + 1] = "<h2>" + line[j + 1]
                            j += 1
                            line.append ("</h2>")
                        
                        elif word in ["@li", "\li"]:
                            line [j] = "<li>"
                            line.append ("</li>")
                            
                        elif word in ["@section", "\section"]:
                            line [j] = ""
                            if nextWord [0] in lowercase and j < (len (line) - 2):
                                line [j + 1] = ""
                                line [j + 2] = "<b>%s" % escapeHtml(line[j + 2])
                                j += 2
                            else:                        
                                line [j + 1] = "<b>%s" % escapeHtml(nextWord)
                                j += 1
                            line.append ("</b>")
                        elif word=='\\image' or word=='@image':
                            line[j] = ''
                            line[j+1] = ''
                            line[j+2] = '<div align="center"><img src="../images/' + line[j+2] + '" /><p><strong>'
                            line.append ('</strong></p></div>')
                            j += 2

                        else:                        
                            line[j] = escapeDoyxgenHtml(line[j])
                    else:
                        line[j] = escapeDoyxgenHtml(line[j])
                    j += 1
                
                line = [word for word in line if word]                           
                newdocline.append(" ".join (line))
            doclines[i] = " ".join(newdocline)
    
        if state==STATE_PARAM:
            doclines.append("</td></tr>")
            state = STATE_PARAM_TRAILING
        if state==STATE_PARAM_TRAILING:
            doclines.append("</table></dl>\n<p>")
        if state==STATE_NBULLET:
            doclines.append("</li>")
            state = STATE_NBULLET_TRAILING
        if state==STATE_NBULLET_TRAILING:
            doclines.append("</ol>\n<p>")
        if state==STATE_DL or state==STATE_LICENSES:
            doclines.append("</dd></dl>")
            
        doclines.append("</p>")
        
        newdoc = "<p>" + "\n".join (doclines)
        newdoc = newdoc.replace ("<p>\n</p>\n", "")
        #newdoc = newdoc.replace ("\n\n", "</p>\n<p>\n")
        return handleTags(newdoc)
        
if __name__ == '__main__':
    r = Reduce()
    print(r.do_txt("""
/**
* The base class for configuration modules.
*
* Configuration modules are realized as plugins that are loaded only when
* needed.
*
* The module in principle is a simple widget displaying the
* item to be changed. The module has a very small interface.
*
* All the necessary glue logic and the GUI bells and whistles
* are provided by the control center and must not concern
* the module author.
*
* To write a config module, you have to create a library
* that contains at one factory function like this:
*
* \code
* #include <kgenericfactory.h>
*
* typedef KGenericFactory<YourKCModule, QWidget> YourKCModuleFactory;
* K_EXPORT_COMPONENT_FACTORY( yourLibName, YourKCModuleFactory("name_of_the_po_file") );
* \endcode
*
* @author Matthias Hoelzer-Kluepfel <hoelzer@kde.org>
*/
"""))
