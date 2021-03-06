# -*- coding: utf-8 -*-
#     Copyright 2008-9 Simon Edwards <simon@simonzone.com>
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

#
# Unit tests for the .sip file parser.
#
import unittest
import sipparser
import sipsymboldata
import os
import os.path
import subprocess
import re

def CleanWhitespace(code):
    return re.sub(r"\s+"," ",code).strip()

class TestSipParser(unittest.TestCase):
    def setUp(self):
        self.parser = sipparser.SipParser()
        self.syms = sipsymboldata.SymbolData()
        
    def mirrorTest(self,code,debugLevel=0):
        scope = self.parser.parse(self.syms, code, debugLevel=debugLevel);
        new_code = scope.format()
        if CleanWhitespace(new_code)!=CleanWhitespace(code):
            self.fail("Output code doesn't match input code.\n---- Original:\n" + code + "\n---- Result:\n" + new_code)

    def ioTest(self,incode,outcode,debugLevel=0):
        scope = self.parser.parse(self.syms, incode, debugLevel=debugLevel);
        new_code = scope.format()
        if CleanWhitespace(new_code)!=CleanWhitespace(outcode):
            self.fail("Output code doesn't match expected output code.\n---- Expected:\n" + outcode + "\n---- Result:\n" + new_code)

    def strictMirrorTest(self,code,debugLevel=0):
        scope = self.parser.parse(self.syms, code, debugLevel=debugLevel);
        new_code = scope.format()
        if new_code!=code:
            self.fail("Output code doesn't match input code.\n---- Original:\n" + code + "\n---- Result:\n" + new_code)

    def simpleParseTest(self,code,debugLevel=0):
        self.parser.parse(self.syms, code, debugLevel=debugLevel);

    def testClass0(self):
        self.mirrorTest(
            """
            class Foo {
            };
            """)

    def testClass1(self):
        self.mirrorTest(
            """
            class Foo {
                Foo ();
            };
            """)

    def testClass3(self):
        self.mirrorTest(
            """
            class Foo : Bar {
            };""")

    def testClass5(self):
        self.mirrorTest(
            """
            class Foo : Bar, Zyzz {
            };""")

    def testClass6(self):
        self.mirrorTest(
            """
            class Foo /Abstract/ {
            };
            """)

    def testClass7(self):
        self.mirrorTest(
            """
            class Foo {
                    Foo (int x);
                public:
                    Foo ();
            };
            """)
    def testClass8(self):
        self.mirrorTest(
            """
class ServiceBase : KShared {
  ServiceBase (ServiceBasePrivate*const d);
};
""")

    def testOpaqueClass(self):
        self.mirrorTest(
            """
            class OpaqueFoo;
            """)

    def testClassVariable(self):
        self.mirrorTest(
            """
            class Foo {
                public:
                    int public_x;
                private:
                    int private_y;
                protected:
                    int protected_z;
            };""")

    def testClassVariable2(self):
        self.mirrorTest(
            """
            class Foo {
                public:
                    int x = 0;
            };""")

    def testClassVariable3(self):
        self.mirrorTest(
            """
            class Foo {
                static int x;
                const int y;
            };""")

    def testClassConstructor2(self):
        self.mirrorTest(
            """
            class Foo {
                Foo (int x, int y);
            };""")

    def testClassConstructor3(self):
        self.mirrorTest(
            """
            class Foo {
                explicit Foo (int x);
            };""")

    def testClassDestructor1(self):
        self.mirrorTest(
            """
            class Foo {
                ~Foo ();
            };""")

    def testClassMethod(self):
        self.mirrorTest(
            """
            class Foo {
                int getFooValue (int x);
            };""")

    def testClassVirtualMethod(self):
        self.mirrorTest(
            """
            class Foo {
                virtual int getFooValue (int x);
            };""")

    def testClassPureVirtualMethod(self):
        self.mirrorTest(
            """
            class Foo {
                virtual int getFooValue (int x)=0;
            };""")

    def testFunctions(self):
        self.mirrorTest(
            """
            int DoFoo (int x);
            void StopFoo ();
            """)

    def testFunctions2(self):
        self.mirrorTest(
            """
            const int* DoFoo (int x);
            """)

    def testFunctions3(self):
        self.mirrorTest(
            """
            QString& FooConst () const;
            """)

    def testFunctions4(self):
        self.mirrorTest(
            """
            void Foo (unsigned long x);
            """)

    def testFunctions5(self):
        self.mirrorTest(
            """
            void Foo (long x [5]);
            """)

    def testFunctions6(self):
        self.mirrorTest(
            """
            void* foo (int, double (*doublePtr)(float,QString*));
            """)

    def testFunctions7(self):
        self.mirrorTest(
            """
            int DoFoo (int* x /Out/);
            """)

    def testFunctions9(self):
        self.mirrorTest(
            """
KConfigGroup            group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group) const;
            """)

    def testFunctions10(self):
        self.mirrorTest(
            """
TermPrivate QSharedDataPointer<Nepomuk::Query::TermPrivate>::clone ();
            """)

    def testAccess(self):
        self.mirrorTest(
            """void PlainPreFunc ();
class Foo {
    public:
        class Bar {
                void privateBar ();
        };
        void publicFoo ();
};
void PlainPostFunc ();
""")
    

    def testFunctionIgnore(self):
        self.mirrorTest(
            """
            void DontIgnoreThisFoo ();
            //ig int DoIgnoreMeFoo (int x);
            void DontIgnoreThisFoo2 ();
            """)
        
    def testOpaqueClassIgnore(self):
        self.mirrorTest(
            """
            //ig class Foo;
            """)
        
    def testTypedefIgnore(self):
        self.mirrorTest(
"""
//ig    typedef QList<KProtocolInfo::Ptr> List;                                                                    
    static QStringList      protocols ();                                                                          
""")

    def testTypedefIgnore2(self):
        self.mirrorTest("""
class KLibrary : QLibrary
{
public:
//ig     typedef void (*void_function_ptr)();
};
""")

    def testOperator1(self):
        self.mirrorTest(
            """
            class Foo {
                bool operator == (int);
            };
            """)

    def testOperator2(self):
        self.mirrorTest(
            """
            class Foo {
                virtual bool operator == (int);
            };
            """)

    def testOperator3(self):
        self.mirrorTest(
            """
            class Foo {
                QVariant operator QVariant ();
            };
            """,debugLevel=0)

    def testNamespace(self):
        self.mirrorTest(
            """
            namespace FooSpace {
                int DoFoo (int x);
                void StopFoo ();
            };
            """)

    def testEnum(self):
        self.mirrorTest(
            """
            enum global {
                earth,
                orb,
                globe
            };
            """)

    def testEnum2(self):
        self.mirrorTest(
            """
            enum global {
                earth,
                orb,
                globe,

                universe
            };
            """)

    def testEnum3(self):
        self.mirrorTest(
            """
            enum global {

                // just a comment.
                earth,
                orb,

                // Wierd stuff.
                globe,
                universe

                // le fin
            };
            """)

    def testEnumAnonymous(self):
        self.mirrorTest(
            """
            enum {
                earth,
                orb,
                globe
            };
            """)

    def testEnumSipIf(self):
        self.ioTest(
            """
enum {
    earth,
    // This is a comment
%If (FOO -)
    orb,
%End
    globe
};
""","""
enum {
    earth,
    // This is a comment
    orb,
    globe
};
            """,debugLevel=0)

    def testTypedef1(self):
        self.mirrorTest(
            """
            typedef QString& stringref;
            """)
    
    def testTypedef2(self):
        self.mirrorTest(
            """typedef QObject** objPtrPtr;
            """)

    def testTypedef3(self):
        self.mirrorTest(
"""
typedef QFlags<KCrash::CrashFlag> CrashFlags;
""")

    def testTypedef4(self):
        self.mirrorTest(
"""
//ig typedef foo bar;
""")

    def testTypedef5(self):
        self.mirrorTest("""
//ig typedef void (*KdeCleanUpFunction)();
""")

    def testSipDirective1(self):
        self.mirrorTest(
            """
class Foo {
    %TypeHeaderCode
    #include <kconfigbase.h>
    %End
};
""")

    def testMethodCode1(self):
        self.mirrorTest(
            """
int DoFoo (int x);
%MethodCode
// Method code is here.

// Ends here.
%End
""")

    def testTemplate(self):
        self.mirrorTest(
            """
            QList<int> intlist;
            """)

    def testLineComment1(self):
        self.mirrorTest(
"""
// Just a line comment.
""")

    def testLineComment2(self):
        self.mirrorTest(
"""
/* Just a C comment. */
""")

    def testBlankLine(self):
        self.mirrorTest(
"""
// Start, then blank
  
// End
""")

    def testBlankLine2(self):
        self.mirrorTest(
"""
class Foo {
%ConvertToSubClassCode

// Subcode...
// End.
%End
};
""")

    def testTemplate(self):
        self.mirrorTest(
"""
template <Bar>
class Foo {
public:
    static QString deref (Bar i);
};
""")

    def testMappedType(self):
        self.mirrorTest(
"""
%MappedType QMap<Foo,Bar>
{

};

""")

    def testMappedType2(self):
        self.mirrorTest(
"""
template <TYPE1,TYPE2>
%MappedType QMap<TYPE1,TYPE2>
{

};

class Foo {

};
""")

    def testMappedType3(self):
     
        self.mirrorTest(
"""
%MappedType QChar /API=QString:2 - /
{
// Foo
};
""",debugLevel=0)

    def testNestedTemplate(self):
        self.mirrorTest(
"""
KBookmarkGroup          addBookmarks (const QList<QPair<QString,QString>>& list);
""")

    def testCppSigs1(self):
        self.mirrorTest("""
class Foo {
        ItemDouble (const QString& _group, const QString& _key, double reference, double defaultValue = 0) [(const QString& _group, const QString& _key, double& reference, double defaultValue = 0)];         
};
""")

    def testCppSigs2(self):
        self.mirrorTest("""
class Foo {
        int itemDouble (const QString& _group, const QString& _key, double reference, double defaultValue = 0)  [int (const QString& _group, const QString& _key, double& reference, double defaultValue = 0)];         
};
""")
    def testCppSigs3(self):
        self.mirrorTest("""
class Foo
{
    virtual SIP_PYOBJECT    read (qint64 maxlen) /ReleaseGIL/ [qint64 (char* data, qint64 maxlen)];
%MethodCode
// foo.
%End
};
""")

    def testForce(self):
        self.mirrorTest("""
class Foo {
public:
    Foo ();
    int bar ();
//force
    int forceBar ();
//end
};
""")

    def testForce2(self):
        self.mirrorTest("""
namespace Foo {
    int bar ();
//force
    int forceBar ();
//end
    int bar2 ();
};
""")

    def testArrowDefaults(self):
        self.mirrorTest("""
class Foo
{
    QString                 label (const QString& language = KGlobal::locale()->language());
};
""")

    def testCTSCC(self):
        self.mirrorTest("""
class Foo {
//force
%ConvertToSubClassCode
// Custom %ConvertToSubClassCode
%End
//end
};
""")

    def testTemplateBlocks(self):
        text ="""
//

%ModuleHeaderCode
#include <kaccelgen.h>
%End

namespace KAccelGen
{

template <Iter>
class Deref
{
%TypeHeaderCode
#include <kaccelgen.h>
%End


public:
    static QString          deref (Iter i);
};
// Deref


template <Iter>
class Deref_Key
{
%TypeHeaderCode
#include <kaccelgen.h>
%End


public:
    static QString          deref (Iter i);
};
// Deref_Key

bool                    isLegalAccelerator (const QString& str, int index);
void                    generate (const QStringList& source, QStringList& target);
};
// KAccelGen

%ModuleHeaderCode
#include <kaccelgen.h>
%End
"""

        self.mirrorTest(text)

#        scope = self.parser.parse(self.syms, text, debugLevel=0);
#        for item in scope[5]:
#            print(repr(item))
#            print("-----------------------------" + item.format())


    def testStrict0(self):
        self.strictMirrorTest(
            """// Foo

// bar

%ModuleHeaderCode
//ctscc
dsfd
%End


class KUrl : QUrl
{
};
""")

    def testSuperClassQueries(self):
        scope = self.parser.parse(self.syms, """
class Bar {};
class Zyzz : Bar {};
class Foo : Zyzz {

};
""")
        bar = self.syms.lookupType("Bar",scope)
        self.assertTrue(bar is not None)
        self.assertTrue(bar.allSuperClassNames() is not None)
        self.assertTrue(len(bar.allSuperClassNames())==0)
        foo = self.syms.lookupType("Foo",scope)
        self.assertTrue(foo is not None)
        fooBases = foo.allSuperClassNames()
        self.assertTrue(fooBases is not None)
        self.assertTrue(len(fooBases)==2)

    def testSipStmt(self):
        scope = self.parser.parse(self.syms, """
template<TYPE1, TYPE2>
%MappedType QHash<TYPE1, TYPE2> /DocType="dict-of-TYPE1-TYPE2"/
{

};

""",debugLevel=0)

    def testModule(self):
        self.mirrorTest("""
%Module PyKDE4.kdecore
""")

    def testModule2(self):
        self.mirrorTest("""
%Module(name=PyQt4.QtCore, keyword_arguments="Optional")

%Timeline {Qt_4_1_1 Qt_4_1_2}""")

    def testAPI(self):
        self.simpleParseTest("""
%API(name=QDate, version=2)
""")

    def testInclude(self):
        self.simpleParseTest("""
%Include(name=staticplugins.sip, optional=True)
""")

    def testGetter(self):
        # This just has to go through the parser. PyKDE doesn't need the info which is read in.
        self.simpleParseTest("""
class Foo {
public:
    static const QMetaObject staticMetaObject {
%GetCode
    sipPy = qpycore_qobject_staticmetaobject(sipPyType);
%End
};
};
""")

    def testQListSubclass(self):
        self.simpleParseTest("""
class AddresseeList : QList<Addressee>
{
};
""")

    def testEnumAnnotation(self):
        self.simpleParseTest("""enum Command
{
    None /PyName=None_/,
    SetTransferMode,
    SetProxy,
    ConnectToHost
};
""")



    def xtestQtCoremod(self):
        with open("/usr/share/sip/PyQt4/QtCore/QtCoremod.sip") as fhandle:
            text = fhandle.read()
        scope = self.parser.parse(self.syms, text)
        print(scope.format())

    def xtestFullCompare(self):
        sipdir = "/home/sbe/devel/svn/kde/branches/KDE/4.4/kdebindings/python/pykde4/sip/kdeui/"
        #sipdir = "/usr/share/sip/PyQt4/QtGui/"        
        for filename in os.listdir(sipdir):
            print(filename)
            if filename.endswith(".sip"):
                filepath = os.path.join(sipdir,filename) 
                with open(filepath) as fhandle:
                    text = fhandle.read()
                self.syms = sipsymboldata.SymbolData()
                scope = self.parser.parse(self.syms, text)

                output = scope.format()
                if CleanWhitespace(text)!=CleanWhitespace(output):
                    with open(filename+".v2",'w') as outhandle:
                        outhandle.write(scope.format())
                    subprocess.call(['diff','-durb',filepath,filename+".v2"])

#        self.parser = sipparser.SipParser()

#    def parse(self,text):
#        self.parser.parse(self.symbol_data, self.state_info, text,2 if debug else 1)
'''
    def testEmpty(self):
        self.parse("")

    def testCComments(self):
        self.parse("""


/* A C style comment */

/*
Multiline
*/


// single
/*
muliple
*/
""")

    def testMappedTypeConstType(self):
        self.parse("""
%MappedType QList<const Soprano::Backend*>
{
%TypeHeaderCode
#include <qlist.h>
%End

%ConvertFromTypeCode
    // Create the list.
%End

%ConvertToTypeCode
    // Check the type if that is all that is required.

%End
};

""")

'''
if __name__ == '__main__':
    unittest.main()
