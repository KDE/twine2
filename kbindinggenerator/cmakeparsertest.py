#!env python3
# -*- coding: utf-8 -*-
#     Copyright 2014 Simon Edwards <simon@simonzone.com>
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
import cmakeparser

class TestCMakeParser(unittest.TestCase):

    def setUp(self):
        self.parser = cmakeparser.CMakeParser()

    def testComment(self):
        self.assertTrue(len(self.parser.parse("""# Just a comment
"""))==0, "Comment failed.")

    def testCommentSpace(self):
        self.assertTrue(len(self.parser.parse("""
# Just a comment

"""))==0, "Comment space failed.")

    def testEmptyStatement(self):
        result = self.parser.parse("""endif()""")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "endif")
        self.assertEqual(len(result[0].arguments()), 0)

    def testStatement(self):
        result = self.parser.parse("""project(pykde5)
""")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "project")

    def testStatement2(self):
        result = self.parser.parse("""project(pykde5) # just a comment
""")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "project")

    def testStatement3(self):
        result = self.parser.parse("""cmake_policy(SET CMP0002 OLD)""")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "cmake_policy")
        self.assertEqual(len(result[0].arguments()), 3)

    def testStatement4(self):
        result = self.parser.parse("""cmake_policy ( SET CMP0002 OLD ) """)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "cmake_policy")
        self.assertEqual(len(result[0].arguments()), 3)

    def testStatement5(self):
        result = self.parser.parse("""include_directories(
    ${SIP_INCLUDE_DIR}
    ${qt5core_include}
    ${qt5gui_include}
    ${qt5widgets_include}
)
""")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "include_directories")
        self.assertEqual(len(result[0].arguments()), 4)

    def testStatement6(self):
        result = self.parser.parse("""include_directories(
    ${SIP_INCLUDE_DIR}
    #${qt5core_include}
    ${qt5gui_include}
    ${qt5widgets_include}
)
""")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].command(), "include_directories")
        self.assertEqual(len(result[0].arguments()), 3)


    def testString(self):
        result = self.parser.parse("""
set_package_properties(PythonLibrary PROPERTIES DESCRIPTION
                       "The Python Library" URL "http://www.python.org"
                       TYPE REQUIRED PURPOSE "Required to build PyKDE4")
""")
        # print(repr(result))

    def testString2(self):
        result = self.parser.parse("""
set_package_properties(PythonLibrary PROPERTIES DESCRIPTION
                       "The Python Library" URL "http://www.python.org"
                       TYPE REQUIRED PURPOSE "Required to build PyKDE4.
                       And some muliline stuff.")
""")
        # print(repr(result))

    def testString3(self):
        result = self.parser.parse("""
    check_cxx_source_compiles("     #ifdef __SUNPRO_CC
                                    #define __asm__ asm
                                    #endif
                    int main() { __asm__(\\"pxor %mm0, %mm0\\") ; }" HAVE_X86_MMX)
""")
        # print(repr(result))
        self.assertEqual(len(result[0].arguments()), 2)

    def testString4(self):
        result = self.parser.parse(r"""
target_compile_definitions(${BACKEND_TEST_TARGET} PUBLIC -DKDIRWATCH_TEST_METHOD=\"${_backendName}\")
""", debug=0)
        #print(repr(result))
        #self.assertEqual(len(result[0].arguments()), 2)


    def testNesting(self):
        result = self.parser.parse("""
        if(MSVC OR (WIN32 AND "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel"))
""")
        self.assertEqual(len(result[0].arguments()), 9)

    def testSolidCmake(self):
        result = self.parser.parse(
"""
include (CheckCXXSourceCompiles)

if(MSVC OR (WIN32 AND "${CMAKE_CXX_COMPILER_ID}" STREQUAL "Intel"))
    check_cxx_source_compiles("int main() { __asm { pxor mm0, mm0 }; }" HAVE_X86_MMX)
else()
    check_cxx_source_compiles("     #ifdef __SUNPRO_CC
                                    #define __asm__ asm
                                    #endif
                    int main() { __asm__(\\"pxor %mm0, %mm0\\") ; }" HAVE_X86_MMX)
endif()
""")

if __name__ == '__main__':
    unittest.main()
