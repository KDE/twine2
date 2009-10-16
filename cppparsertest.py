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

import unittest
import cppparser
import cppsymboldata
import qtkdemacros

class TestCppParser(unittest.TestCase):

    def setUp(self):
        self.parser = cppparser.CppParser()
        self.syms = cppsymboldata.SymbolData()

    def testClass1(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
            };
            """)
        print(scope.format())
        #self.assertEqual(self.seq, range(10))

    def testClass2(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                public:
            };""")
        print(scope.format())

    def testClass3(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo : public Bar {
            };""")
        print(scope.format())

    def testClass4(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo : private Bar {
            };""")
        print(scope.format())

    def testClass5(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo : Bar, Zyzz {
            };""")
        print(scope.format())

    def testClass6(self):
        scope = self.parser.parse(self.syms,
            """
            class OpaqueFoo;
            """)
        print(scope.format())

    def testClassVariable(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                public:
                    int public_x;
                private:
                    int private_y;
                protected:
                    int protected_z;
            };""")
        print(scope.format())

    def testClassVariable2(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                public:
                    int x=0;
            };""")
        print(scope.format())

    def testClassVariable3(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                static int x;
                const int y;
            };""")
        print(scope.format())

    def testClassConstructor(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                Foo();
            };""")
        print(scope.format())

    def testClassConstructor2(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                Foo(int x,int y);
            };""")
        print(scope.format())

    def testClassConstructor3(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                explicit Foo(int x);
            };""")
        print(scope.format())

    def testClassConstructor4(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                public:
                    Foo();
                private:
                    Foo(int x);
            };""")
        print(scope.format())

    def testClassDestructor1(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                ~Foo();
            };""")
        print(scope.format())

    def testClassMethod(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                int getFooValue(int x);
            };""")
        print(scope.format())

    def testClassVirtualMethod(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                virtual int getFooValue(int x);
            };""")
        print(scope.format())

    def testClassPureVirtualMethod(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                virtual int getFooValue(int x)=0;
            };""")
        print(scope.format())

    def testFunctions(self):
        scope = self.parser.parse(self.syms,
            """
            int DoFoo(int x);
            void StopFoo();
            """)
        print(scope.format())

    def testFunctions2(self):
        scope = self.parser.parse(self.syms,
            """
            const int *DoFoo(int x);
            """)
        print(scope.format())

    def testFunctions3(self):
        scope = self.parser.parse(self.syms,
            """
            QString& FooConst() const;
            """)
        print(scope.format())

    def testFunctions4(self):
        scope = self.parser.parse(self.syms,
            """
            void Foo(unsigned long x);
            """)
        print(scope.format())

    def testFunctions5(self):
        scope = self.parser.parse(self.syms,
            """
            void Foo(long x[5]);
            """)
        print(scope.format())

    def testFunctions6(self):
        scope = self.parser.parse(self.syms,
            """
            void* foo (int, double (*doublePtr)(float, QString*));
            """)
        print(scope.format())

    def testFunctions7(self):
        scope = self.parser.parse(self.syms,
            """
            template <T>
            void foo (T t);
            """)
        print(scope.format())
        
    def testFunctions8(self):
        scope = self.parser.parse(self.syms,
            """
template<typename T>
    inline T readCheck(const char *key, const T &defaultValue) const;
            """)
        print(scope.format())

    def testFunctions9(self):
        scope = self.parser.parse(self.syms,
            """
KConfigGroup            group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group) const;
            """)
        print(scope.format())


    def testOperator1(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                bool operator == (int);
            };
            """)
        print(scope.format())


    def testNamespace(self):
        scope = self.parser.parse(self.syms,
            """
            namespace FooSpace {
                int DoFoo(int x);
                void StopFoo();
            }
            """)
        print(scope.format())

    def testEnum(self):
        scope = self.parser.parse(self.syms,
            """
            enum global {
                earth,
                orb,
                globe
            };
            """)
        print(scope.format())

    def testEnumInClass(self):
        scope = self.parser.parse(self.syms,
            """
enum TimeFormatOption {
    TimeDefault        = 0x0,   ///< Default formatting using seconds and the format
                                ///< as specified by the locale.
    TimeDuration       = 0x6   ///< Read/format time string as duration. This will strip
};
              """,debugLevel=0)
        print(scope.format())

    def testNamespaceEnum(self):
        scope = self.parser.parse(self.syms,
            """
namespace Foo {

    const KComponentData &mainComponent();

    enum global {
        earth,
        orb,
        globe
    };
}
            """,debugLevel=0)
        print(scope.format())


    def testEnumAnonymous(self):
        scope = self.parser.parse(self.syms,
            """
            enum {
                earth,
                orb,
                globe
            };
            """)
        print(scope.format())

    def testFriendClass(self):
        scope = self.parser.parse(self.syms,
            """
            class Foo {
                friend class Bar;
            };
            """)
        print(scope.format())

    def testTypedef1(self):
        scope = self.parser.parse(self.syms,
            """
            typedef QString& stringref;
            """)
        print(scope.format())

    def testTypedef2(self):
        scope = self.parser.parse(self.syms,
            """
            typedef enum simple {easy, bobsyouruncle, noproblem};
            """)
        print(scope.format())
    
    def testTypedef3(self):
        scope = self.parser.parse(self.syms,
            """typedef QObject** objPtrPtr;
            """)
        print(scope.format())

    def testTypedef4(self):
        scope = self.parser.parse(self.syms,
            """typedef QObject *(*CreateInstanceFunction)(QWidget *, QObject *, const QVariantList &);
            """)
        print(scope.format())

    def testTypedef5(self):
        scope = self.parser.parse(self.syms,
            """typedef QFlags< SearchOption > SearchOptions;
            """)
        print(scope.format())
        
    def testTypedef6(self):
        scope = self.parser.parse(self.syms,
            """typedef enum { Name, FromUrl } FileNameUsedForCopying;
            """)
        print(scope.format())

    def testTypedef7(self):
        scope = self.parser.parse(self.syms,
            """typedef enum { Name, FromUrl } FileNameUsedForCopying;
            """)
        print(scope.format())

    def testTemplate(self):
        scope = self.parser.parse(self.syms,
            """
            QList<int> intlist;
            """)
        print(scope.format())

    def testInline(self):
        scope = self.parser.parse(self.syms,
            """
            inline operator bool() const { return ( d != 0 ); }
            """,debugLevel=2)
        print(scope.format())

    def testMacro(self):
        self.parser.bareMacros = ["Q_OBJECT"]
        scope = self.parser.parse(self.syms,
            """
            class FooWidget : public QObject {
                    Q_OBJECT
                public:
                    FooWidget();
            };
            """)
        print(scope.format())

    def testMacro2(self):
        self.parser.bareMacros = ["FOO_EXPORT"]
        scope = self.parser.parse(self.syms,
            """
            class FOO_EXPORT FooWidget {
            };
            """)
        print(scope.format())

    def testMacro3(self):
        self.parser.macros = ["Q_DISABLE_COPY"]
        scope = self.parser.parse(self.syms,
            """
            class FooWidget {
                public:
                    Foo();
                private:
                    Q_DISABLE_COPY( FooWidget )
            };
            """)
        print(scope.format())

    def testMacro4(self):
        self.parser.bareMacros = ["KGGZMOD_EXPORT"]
        scope = self.parser.parse(self.syms,
            """
class Module
{
public:
    Module(const QString &name);
    ~Module();

    enum State
    {
            created,
            done
    };
};
            """)
        print(scope.format())

    def testBitfield(self):
        scope = self.parser.parse(self.syms,
            """
            bool mHasMin : 1;
            """,debugLevel=2)
        print(scope.format())

    def testAccess(self):
        scope = self.parser.parse(self.syms,
            """void PlainPreFunc ();
class Foo {
    public:
        class Bar {
            private:
                void privateBar ();
        };
        void publicFoo ();
};
void PlainPostFunc ();
""")
        print(scope.format())

    def testLiveAmmo(self):
        with open("/home/sbe/devel/svn/kde/branches/KDE/4.3/kdeedu/marble/src/lib/MarbleMap.h") as fhandle:
            text = fhandle.read()
        self.parser.bareMacros = qtkdemacros.QtBareMacros(["MARBLE_EXPORT"])
        self.parser.macros = qtkdemacros.QtMacros()
        self.parser.preprocessorSubstitutionMacros = qtkdemacros.QtPreprocessSubstitutionMacros()
        scope = self.parser.parse(self.syms, text)
        print(scope.format())


if __name__ == '__main__':
    unittest.main()
