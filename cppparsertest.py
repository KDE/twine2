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

    def testClass1(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                public:
            };""")
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

    def testFunctions(self):
        self.parser.parse(self.syms,
            """
            int DoFoo(int x);
            void StopFoo();
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


if __name__ == '__main__':
    unittest.main()
