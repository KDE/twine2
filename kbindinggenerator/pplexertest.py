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
import pplexer

class TestPpParser(unittest.TestCase):
#    def setUp(self):
#        self.parser = ppparser.PpParser()
#        self.syms = cppsymboldata.SymbolData()

    def testFixDoc(self):
        print(pplexer.fixDoc("""
enum TimeFormatOption {
    TimeDefault        = 0x0,   ///< Default formatting using seconds and the format
                                ///< as specified by the locale.
    TimeDuration       = 0x6   ///< Read/format time string as duration. This will strip
};
""".split('\n')))#,[],[]))

    def testDefinesFunction(self):
        print(pplexer.preprocess("""
            /**
             * http://freedesktop.org/standards/xesam/1.0/core#definesClass 
             * 
             * Source code defines class 
             */
            SOPRANO_EXPORT QUrl definesClass();

"""))

    def testDefinesFunction2(self):
        print(pplexer.preprocess("""/*
 * foo
 */

#ifndef _SOPRANO_SERVER_DBUS_CLIENT_H_
#define _SOPRANO_SERVER_DBUS_CLIENT_H_

#include <QtCore/QObject>

#include "backend.h"
#include "error.h"
#include "soprano_export.h"

namespace Soprano {

    class Model;

};
#endif 
"""))

    def testComments(self):
        print(pplexer.preprocess("""
class Foo {
public:
    /**
     * bar docs.
     */
    void bar();
};

"""))


if __name__ == '__main__':
    unittest.main()
