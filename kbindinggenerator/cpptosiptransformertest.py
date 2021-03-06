# -*- coding: utf-8 -*-
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

#
# Unit tests for the Cpp to Sip transformer.
#
import unittest
import cppparser
import cppsymboldata
import cpptosiptransformer
import sipparser
import sipsymboldata

class TestCppToSipTransformer(unittest.TestCase):
    def setUp(self):
        pass
        
    def convert(self, cpptext, exportMacros=None, ignoreBases=None):
        parser = cppparser.CppParser()
        if exportMacros is not None:
            parser.bareMacros = exportMacros
            
        syms = cppsymboldata.SymbolData()
        scope = parser.parse(syms,cpptext)
        print("Cpp----------------------------------")
        print(scope.format())
        
        transformer = cpptosiptransformer.CppToSipTransformer()
        transformer.setExportMacros(exportMacros)
        transformer.setIgnoreBaseClasses(ignoreBases)
        
        sipsym = sipsymboldata.SymbolData()
        sipscope = transformer.convert(scope,sipsym)
        print("Sip----------------------------------")
        print(sipscope.format())
        return sipscope
        
    def annotate(self, siptext, rules):
        parser = sipparser.SipParser()
        syms = sipsymboldata.SymbolData()
        scope = parser.parse(syms,siptext)
        
        print("Sip----------------------------------")
        print(scope.format())
        annotator = cpptosiptransformer.SipAnnotator()
        annotator.setMethodAnnotationRules(rules)
        annotator.applyRules(scope)
        
        print("Sip output---------------------------")
        print(scope.format())
        
    def sanityCheck(self, siptext):
        parser = sipparser.SipParser()
        syms = sipsymboldata.SymbolData()
        scope = parser.parse(syms,siptext)
        
        cpptosiptransformer.SanityCheckSip(syms,[scope])
        print("Sip----------------------------------")
        print(scope.format())
        
    def expandClassNames(self, siptext):
        parser = sipparser.SipParser()
        syms = sipsymboldata.SymbolData()
        scope = parser.parse(syms,siptext)
        
        print("Sip----------------------------------")
        print(scope.format())
        cpptosiptransformer.ExpandClassNames(syms,scope)
        
        print("Sip output---------------------------")
        print(scope.format())        
        
    def testConstructor(self):
        self.convert("""
#include <foo.h>
class EXPORT_FOO Foo {
public:
    Foo();
};
""",exportMacros=["EXPORT_FOO"])

    def testConstructor2(self):
        self.convert("""
#include <foo.h>
class EXPORT_FOO Foo {
public:
    Foo();
protected:
    Foo(int x);
   
};
""",exportMacros=["EXPORT_FOO"])

    def testClass(self):
        self.convert("""
class Foo {
public:
    Foo();
    int bar(int x);
};
""")

    def testClass2(self):
        self.convert("""
class Foo : public Bar {
public:
    Foo();
};
""")

    def testVariable(self):
        self.convert("""
int bar;
""")

    def testStaticVariable(self):
        self.convert("""
static int staticBar;
""")

    def testFunction(self):
        self.convert("""
int FunctionBar();
""")

    def testConstFunctions(self):
        self.convert("""
KConfigGroup            group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group) const;
""")



    def testStaticFunction(self):
        self.convert("""
static int StaticFunctionBar();
""")

    def testNamespace(self):
        self.convert("""
namespace FooSpace {
    int bar;
}
""")
    
    def testEnum(self):
        self.convert("""
enum global {
    earth,
    orb,
    globe
};
""")
        
    def testEnumTypedef(self):
        self.convert("""
typedef enum {
    earth,
    orb,
    globe
} global;
""")

    def testPrivate(self):
        self.convert("""
class Foo {
public:
    Foo();
    int bar();
    
private:
    int barzor();
   
};
""")

    def testOperators(self):
        self.convert("""
class Foo {
public:
    Foo();
    int operator /(int div);
    
    int operator ++();
   
};
""")

    def testArgumentTypes(self):
        self.convert("""
short int port;
""")

    def testDefaultArgs(self):
        self.convert("""
class Foo {
public:
    int port(bool frazzle=true);
};
""")

    def testTypedef(self):
        self.convert("""
typedef QFlags< SearchOption > SearchOptions;
""")

    ###########################################################################
    def testAnnotate(self):
        self.annotate("""
class Foo {
    public:
        Foo(QWidget *parent);
};
""",
        [cpptosiptransformer.MethodAnnotationRule("ctor","QWidget*","parent","Transfer")])

    def testIgnoreBases(self):
        self.convert("""

class Foo : public Bar, public Zyzz {
   
};
""",ignoreBases=["Zyzz"])

    def testPrivateVars(self):
        self.convert("""
class Statistics {
private:
    StatisticsPrivate* d;
};
""")

    def testOpaqueClasses(self):
        self.convert("""
class Statistics;
""")

    def testNamespaces(self):
        self.convert("""
namespace FooSpace {
    class Bar {
    };
    class Zyzz : public Bar {
    };
}
""")

    def testNestedTemplate(self):
        self.convert("""
KBookmarkGroup addBookmarks(const QList< QPair<QString, QString>> & list);
""")

    def testCTSCC(self):
        parser = sipparser.SipParser()
        syms = sipsymboldata.SymbolData()
        globalScope = parser.parse(syms,"""
class QWidget {};
class QObject {};
class QBar : QWidget {};
""",filename="qtcore.h")
        scope = parser.parse(syms,"""
class KFoo {
};
class KFooSub : KFoo {
};
class KBarWidget : QBar {
};

class KBarWidgetSpecial : KBarWidget {

};
class KSteelBar : QBar {};
class KBob : QObject {};
""",filename="stuff.h")
        annotator = cpptosiptransformer.SipAnnotator()
        cpptosiptransformer.UpdateConvertToSubClassCodeDirectives(syms,[scope],["Zyzz"])
        
        print("Sip----------------------------------")
        print(scope.format())

    def testCTSCC2(self):
        parser = sipparser.SipParser()
        syms = sipsymboldata.SymbolData()
        globalScope = parser.parse(syms,"""
class QWidget {};
""")
        scope = parser.parse(syms,"""
namespace FooSpace {
    class Foo : QWidget {
    };
};
""")
        annotator = cpptosiptransformer.SipAnnotator()
        cpptosiptransformer.UpdateConvertToSubClassCodeDirectives(syms,[scope],["Zyzz"])
        
        print("Sip----------------------------------")
        print(scope.format())

    def testClassNameExpand(self):
        self.expandClassNames("""
namespace FooSpace {
    class Foo { };
    class Bar : Foo { };
};
""")

    def testClassNameExpand2(self):
        self.expandClassNames("""
namespace FooSpace {
    class Foo { };
    class Bar {
        Foo doFooz(Foo inputFoo);
        Foo doFoozRef(Foo &inputFoo);
    };
};
""")

    def testClassNameExpandVars(self):
        self.expandClassNames("""
namespace FooSpace {
    class Foo { };
    class Bar {
        static const Foo fodo;
        Foo doFooz(Foo inputFoo);
        Foo doFoozRef(Foo &inputFoo);
    };
};
""")

    def testSanityCheck(self):
        self.sanityCheck("""
class Foo : QWidget {};
""")

    def testSanityCheck2(self):
        self.sanityCheck("""
void badFoo(int& bar);
void goodFoo(int& bar /In/);
""")


if __name__ == '__main__':
    unittest.main()
