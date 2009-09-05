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
        self.parser.parse(self.syms,
            """
            class Foo {
            };
            """)
        print(self.syms.topScope().format())
        #self.assertEqual(self.seq, range(10))

    def testClass2(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                public:
            };""")
        print(self.syms.topScope().format())

    def testClass3(self):
        self.parser.parse(self.syms,
            """
            class Foo : public Bar {
            };""")
        print(self.syms.topScope().format())

    def testClass4(self):
        self.parser.parse(self.syms,
            """
            class Foo : private Bar {
            };""")
        print(self.syms.topScope().format())

    def testClass5(self):
        self.parser.parse(self.syms,
            """
            class Foo : Bar, Zyzz {
            };""")
        print(self.syms.topScope().format())

    def testClass6(self):
        self.parser.parse(self.syms,
            """
            class OpaqueFoo;
            """)
        print(self.syms.topScope().format())


    def testClassVariable(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                public:
                    int public_x;
                private:
                    int private_y;
                protected:
                    int protected_z;
            };""")
        print(self.syms.topScope().format())

    def testClassVariable2(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                public:
                    int x=0;
            };""")
        print(self.syms.topScope().format())

    def testClassVariable3(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                static int x;
                const int y;
            };""")
        print(self.syms.topScope().format())

    def testClassConstructor(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                Foo();
            };""")
        print(self.syms.topScope().format())

    def testClassConstructor2(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                Foo(int x,int y);
            };""")
        print(self.syms.topScope().format())

    def testClassConstructor3(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                explicit Foo(int x);
            };""")
        print(self.syms.topScope().format())

    def testClassConstructor4(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                public:
                    Foo();
                private:
                    Foo(int x);
            };""")
        print(self.syms.topScope().format())

    def testClassDestructor1(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                ~Foo();
            };""")
        print(self.syms.topScope().format())

    def testClassMethod(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                int getFooValue(int x);
            };""")
        print(self.syms.topScope().format())

    def testClassVirtualMethod(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                virtual int getFooValue(int x);
            };""")
        print(self.syms.topScope().format())

    def testClassPureVirtualMethod(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                virtual int getFooValue(int x)=0;
            };""")
        print(self.syms.topScope().format())

    def testFunctions(self):
        self.parser.parse(self.syms,
            """
            int DoFoo(int x);
            void StopFoo();
            """)
        print(self.syms.topScope().format())

    def testFunctions2(self):
        self.parser.parse(self.syms,
            """
            const int *DoFoo(int x);
            """)
        print(self.syms.topScope().format())

    def testFunctions3(self):
        self.parser.parse(self.syms,
            """
            QString& FooConst() const;
            """)
        print(self.syms.topScope().format())

    def testFunctions4(self):
        self.parser.parse(self.syms,
            """
            void Foo(unsigned long x);
            """)
        print(self.syms.topScope().format())

    def testFunctions5(self):
        self.parser.parse(self.syms,
            """
            void Foo(long x[5]);
            """)
        print(self.syms.topScope().format())

    def testFunctions6(self):
        self.parser.parse(self.syms,
            """
            void* foo (int, double (*doublePtr)(float, QString*));
            """)
        print(self.syms.topScope().format())

    def testOperator1(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                bool operator == (int);
            };
            """)
        print(self.syms.topScope().format())


    def testNamespace(self):
        self.parser.parse(self.syms,
            """
            namespace FooSpace {
                int DoFoo(int x);
                void StopFoo();
            }
            """)
        print(self.syms.topScope().format())

    def testEnum(self):
        self.parser.parse(self.syms,
            """
            enum global {
                earth,
                orb,
                globe
            };
            """)
        print(self.syms.topScope().format())

    def testEnumAnonymous(self):
        self.parser.parse(self.syms,
            """
            enum {
                earth,
                orb,
                globe
            };
            """)
        print(self.syms.topScope().format())

    def testFriendClass(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                friend class Bar;
            };
            """)
        print(self.syms.topScope().format())

    def testTypedef1(self):
        self.parser.parse(self.syms,
            """
            typedef QString& stringref;
            """)
        print(self.syms.topScope().format())

    def testTypedef2(self):
        self.parser.parse(self.syms,
            """
            typedef enum simple {easy, bobsyouruncle, noproblem};
            """)
        print(self.syms.topScope().format())
    
    def testTypedef3(self):
        self.parser.parse(self.syms,
            """typedef QObject** objPtrPtr;
            """)
        print(self.syms.topScope().format())

    def testTemplate(self):
        self.parser.parse(self.syms,
            """
            QList<int> intlist;
            """)
        print(self.syms.topScope().format())

    def testMacro(self):
        self.parser.bareMacros = ["Q_OBJECT"]
        self.parser.parse(self.syms,
            """
            class FooWidget : public QObject {
                    Q_OBJECT
                public:
                    FooWidget();
            };
            """)
        print(self.syms.topScope().format())

    def testMacro2(self):
        self.parser.bareMacros = ["FOO_EXPORT"]
        self.parser.parse(self.syms,
            """
            class FOO_EXPORT FooWidget {
            };
            """)
        print(self.syms.topScope().format())

    def testMacro3(self):
        self.parser.macros = ["Q_DISABLE_COPY"]
        self.parser.parse(self.syms,
            """
            class FooWidget {
                public:
                    Foo();
                private:
                    Q_DISABLE_COPY( FooWidget )
            };
            """)
        print(self.syms.topScope().format())


    def testLiveAmmo(self):
        with open("/home/sbe/devel/svn/kde/branches/KDE/4.3/kdeedu/marble/src/lib/MarbleMap.h") as fhandle:
            text = fhandle.read()
        self.parser.bareMacros = qtkdemacros.QtBareMacros(["MARBLE_EXPORT"])
        self.parser.macros = qtkdemacros.QtMacros()
        self.parser.preprocessorSubstitutionMacros = qtkdemacros.QtPreprocessSubstitutionMacros()
        self.parser.parse(self.syms, text)
        print(self.syms.topScope().format())


if __name__ == '__main__':
    unittest.main()
