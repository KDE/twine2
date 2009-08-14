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
#import stateInfo

#debug = False

class TestSipParser(unittest.TestCase):
    def setUp(self):
        self.parser = sipparser.SipParser()
        self.syms = sipsymboldata.SymbolData()

    def testClass0(self):
        self.parser.parse(self.syms,
            """
            class Foo {
            };
            """)
        print(self.syms.topScope().format())

    def testClass1(self):
        self.parser.parse(self.syms,
            """
            class Foo {
                Foo();
            };
            """)
        print(self.syms.topScope().format())

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
            class Foo : Bar {
            };""")
        print(self.syms.topScope().format())

    def testClass5(self):
        self.parser.parse(self.syms,
            """
            class Foo : Bar, Zyzz {
            };""")
        print(self.syms.topScope().format())

    def testOpaqueClass(self):
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
