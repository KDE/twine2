#     Copyright 2008 Simon Edwards <simon@simonzone.com>
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
import symboldata
import stateInfo

debug = False

class TestSipParser(unittest.TestCase):
    def setUp(self):
        self.parser = sipparser.SipParser()
        self.symbol_data = symboldata.Data()
        self.state_info = stateInfo.StateInfo()

    def parse(self,text):
        self.parser.parse(self.symbol_data, self.state_info, text,2 if debug else 1)

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


if __name__ == '__main__':
    unittest.main()
