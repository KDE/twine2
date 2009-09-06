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

class TestCppToSipTransformer(unittest.TestCase):
    def setUp(self):
        pass
        
    def convert(self, cpptext, exportMacros=None):
        parser = cppparser.CppParser()
        if exportMacros is not None:
            parser.bareMacros = exportMacros
            
        syms = cppsymboldata.SymbolData()
        parser.parse(syms,cpptext)
        print("Cpp----------------------------------")
        print(syms.topScope().format())
        
        transformer = cpptosiptransformer.CppToSipTransformer()
        transformer.setExportMacros(exportMacros)
        siptree = transformer.convert(syms)
        print("Sip----------------------------------")
        print(siptree.topScope().format())
        return siptree
        
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


if __name__ == '__main__':
    unittest.main()
