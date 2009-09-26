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
import sipparser
import sipsymboldata
import sipmerger

class TestSipMerger(unittest.TestCase):
    def merge(self, primarySipText, updateSipText):
        parser = sipparser.SipParser()
        syms = sipsymboldata.SymbolData()
        primaryScope = parser.parse(syms,primarySipText)
        updateScope = parser.parse(syms,updateSipText)
        
        print("Primary Sip -------------------------------------")
        print(primaryScope.format())
        print("Update Sip -------------------------------------")
        print(updateScope.format())
        
        sipmerger.MergeSipScope(syms,primaryScope,updateScope)
        
        print("Result --------------------------------------")
        print(primaryScope.format())
        return primaryScope
        
    def testNewFunction(self):
        newScope = self.merge("""
void foo();
        ""","""
void foo();
void bar();
        """)
        self.assertTrue(len(newScope)==3)
        
    def testFunctionIgnore(self):
        newScope = self.merge("""
//ig void foo();
        ""","""
void foo();
        """)
        fooFunc = newScope[1]
        self.assertTrue(fooFunc.name()=="foo")
        self.assertTrue(fooFunc.ignore())
        
    def testFunctionIgnore2(self):
        newScope = self.merge("""
//ig void foo();
void foo(int x);
        ""","""
void foo();
void foo(int x);
        """)
        fooFunc = newScope[1]
        self.assertTrue(fooFunc.name()=="foo")
        self.assertTrue(fooFunc.ignore())
        fooFunc = newScope[2]
        self.assertTrue(fooFunc.name()=="foo")
        self.assertTrue(not fooFunc.ignore())
        
    def testFunctionAnnotations(self):
        newScope = self.merge("""
void foo() /PyName=Foozor/;
        ""","""
void foo() /Factory/;
        """)
        fooFunc = newScope[1]
        self.assertTrue(len(fooFunc.annotations())==2)

    def testFunctionForce(self):
        newScope = self.merge("""
//force
void foo();
//end
        ""","""
void foo();
        """)
        fooFunc = newScope[1]
        self.assertTrue(fooFunc.force())

    def testFunctionMethodCode(self):
        newScope = self.merge("""
void foo();
%MethodCode
// Method code goes here.
%End
        ""","""
void foo();
        """)
        fooFunc = newScope[1]
        self.assertTrue(len(fooFunc.blocks())==1)

    def testFunctionArguments(self):
        newScope = self.merge("""
void foo(int &x /Out/);
        ""","""
void foo(int &x);
        """)
        fooFunc = newScope[1]
        #self.assertTrue(len(fooFunc.blocks())==1)

    def testConstructor(self):
        newScope = self.merge("""
class Foo {
    Foo() /Default/;
};
        ""","""
class Foo {
    Foo();
};
        """)
        fooCtor = newScope[1][0]
        self.assertTrue(len(fooCtor.annotations())==1)

    def testClass(self):
        newScope = self.merge("""
class Foo /Abstract/ {
};
        ""","""
class Foo {
};
        """)
        fooClass = newScope[1]
        self.assertTrue(len(fooClass.annotations())==1)

    def testClassFunction(self):
        newScope = self.merge("""
class Foo {
  void bar() /Factory/;
};
        ""","""
class Foo {
  void bar();
};
        """)
        fooCtor = newScope[1][0]
        self.assertTrue(len(fooCtor.annotations())==1)

    def testNamespace(self):
        newScope = self.merge("""
namespace Foo {
  void bar() /Factory/;
};
        ""","""
namespace Foo {
  void bar();
};
        """)

    def testForceFunction(self):
        newScope = self.merge("""
void foo();
//force
void bar();
//end
        ""","""
void foo();
        """)



if __name__ == '__main__':
    unittest.main()
