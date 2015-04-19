#!env python3
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
import re

def CleanWhitespace(code):
    return re.sub(r"\s+"," ",code).strip()

class TestCppParser(unittest.TestCase):

    def setUp(self):
        self.parser = cppparser.CppParser()
        self.syms = cppsymboldata.SymbolData()

    def mirrorTest(self,code,debugLevel=0):
        scope = self.parser.parse(self.syms, code, debugLevel=debugLevel);
        new_code = scope.format()
        if CleanWhitespace(new_code)!=CleanWhitespace(code):
            self.fail("Output code doesn't match input code.\n---- Original:\n" + code + "\n---- Result:\n" + new_code)

    def ioTest(self,incode,outcode,debugLevel=0):
        scope = self.parser.parse(self.syms, incode, debugLevel=debugLevel);
        new_code = scope.format()
        if CleanWhitespace(new_code)!=CleanWhitespace(outcode):
            self.fail("Output code doesn't match expected output code.\n---- Expected:\n" + outcode + "\n---- Result:\n" + new_code)

    def testClass1(self):
        self.mirrorTest(
            """
            class Foo {
            };
            """)

    def testClass2(self):
        self.ioTest(
            """
            class Foo {
                public:
            };""","""
            class Foo {
            };""")

    def testClass3(self):
        self.ioTest(
            """
            class Foo : public Bar {
            };""","""
            class Foo : Bar {
            };""")

    def testClass4(self):
        self.ioTest(
            """
            class Foo : private Bar {
            };""","""
            class Foo : Bar {
            };""")

    def testClass5(self):
        self.mirrorTest(
            """
            class Foo : Bar, Zyzz {
            };""")

    def testClass6(self):
        self.mirrorTest(
            """
            class OpaqueFoo;
            """)

    def testClassVariable(self):
        self.mirrorTest(
            """
            class Foo {
                public:
                    int public_x;
                private:
                    int private_y;
                protected:
                    int protected_z;
            };""")

    def testClassVariable2(self):
        self.mirrorTest(
            """
            class Foo {
                public:
                    int x = 0;
            };""")

    def testClassVariable3(self):
        self.mirrorTest(
            """
            class Foo {
                static int x;
                const int y;
            };""")

    def testClassConstructor(self):
        self.mirrorTest(
            """
            class Foo {
                Foo ();
            };""")

    def testClassConstructor2(self):
        self.mirrorTest(
            """
            class Foo {
                Foo (int x, int y);
            };""")

    def testClassConstructor3(self):
        self.mirrorTest(
            """
            class Foo {
                explicit Foo (int x);
            };""")

    def testClassConstructor4(self):
        self.mirrorTest(
            """
            class Foo {
                public:
                    Foo ();
                private:
                    Foo (int x);
            };""")

    def testClassDestructor1(self):
        self.mirrorTest(
            """
            class Foo {
                ~Foo ();
            };""")

    def testClassMethod(self):
        self.mirrorTest(
            """
            class Foo {
                int getFooValue (int x);
            };""")

    def testClassVirtualMethod(self):
        self.mirrorTest(
            """
            class Foo {
                virtual int getFooValue (int x);
            };""")

    def testClassPureVirtualMethod(self):
        self.mirrorTest(
            """
            class Foo {
                virtual int getFooValue (int x)=0;
            };""")

    def testFunctions(self):
        self.mirrorTest(
            """
            int DoFoo (int x);
            void StopFoo ();
            """)

    def testFunctions2(self):
        self.mirrorTest(
            """
            const int* DoFoo (int x);
            """)

    def testFunctions3(self):
        self.mirrorTest(
            """
            QString& FooConst () const;
            """)

    def testFunctions4(self):
        self.mirrorTest(
            """
            void Foo (unsigned long x);
            """)

    def testFunctions5(self):
        self.mirrorTest(
            """
            void Foo (long x [5]);
            """)

#     def testFunctions6(self):
#         self.ioTest(
#             """
#             void* foo (int, double (*doublePtr)(float, QString*));
#             ""","""
# void* foo (int, $fpdouble (* doublePtr = float,QString*);
#             """)

    def testFunctions7(self):
        self.mirrorTest(
            """
            template <T>
            void foo (T t);
            """)
        
    def testFunctions8(self):
        self.ioTest(
            """template<typename T>
inline T readCheck(const char *key, const T &defaultValue) const;
            ""","""template <T>
 T                      readCheck (const char* key, const T& defaultValue) const;
""")

    def testFunctions9(self):
        self.mirrorTest(
            """
KConfigGroup            group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group);
const KConfigGroup      group (const QByteArray& group) const;
            """)

    def testFunctions10(self):
        self.ioTest("""int downloadRegionDialog(WindowFlags const f = 0);""",
          """ int downloadRegionDialog (const WindowFlags f = 0);""")

    def testOperator1(self):
        self.mirrorTest(
            """
            class Foo {
                bool operator== (int);
            };
            """)

    def testNamespace(self):
        self.mirrorTest(
            """
            namespace FooSpace
            {
            int DoFoo (int x);
            void StopFoo ();
            };
            """)

    def testEnum(self):
        self.mirrorTest(
            """
            enum global {
                earth,
                orb,
                globe
            };
            """)

    def testEnumInClass(self):
        self.ioTest(
            """
enum TimeFormatOption {
    TimeDefault        = 0x0,   ///< Default formatting using seconds and the format
                                ///< as specified by the locale.
    TimeDuration       = 0x6   ///< Read/format time string as duration. This will strip
};
              ""","""
enum TimeFormatOption {
    TimeDefault=0x0,
    TimeDuration=0x6
};
              """)

    def testNamespaceEnum(self):
        self.mirrorTest(
            """
namespace Foo {

    const KComponentData& mainComponent ();

    enum global {
        earth,
        orb,
        globe
    };
};
            """)

    def testEnumAnonymous(self):
        self.mirrorTest(
            """
            enum {
                earth,
                orb,
                globe
            };
            """)

    def testFriendClass(self):
        self.ioTest(
            """
            class Foo {
                friend class Bar;
            };
            ""","""
            class Foo {
            };
            """)

    def testTypedef1(self):
        self.mirrorTest(
            """
            typedef QString& stringref;
            """)

    def testTypedef2(self):
        self.ioTest(
            """
            typedef enum simple {easy, bobsyouruncle, noproblem};
            ""","""
            typedef enum
            {
                easy,
                bobsyouruncle,
                noproblem
            } simple;
            """)
    
    def testTypedef3(self):
        self.mirrorTest(
            """typedef QObject** objPtrPtr;
            """)

    def testTypedef4(self):
        self.mirrorTest(
            """typedef QObject* (*CreateInstanceFunction)(QWidget*,QObject*,const QVariantList&);
            """)

    def testTypedef5(self):
        self.mirrorTest(
            """typedef QFlags<SearchOption> SearchOptions;
            """)
        
    def testTypedef6(self):
        self.mirrorTest(
            """typedef enum { Name, FromUrl } FileNameUsedForCopying;
            """)

    def testTypedef7(self):
        self.mirrorTest(
            """typedef enum { Name, FromUrl } FileNameUsedForCopying;
            """)

    def testTemplate(self):
        self.mirrorTest(
            """
            QList<int> intlist;
            """)

    def testInline(self):
        self.ioTest(
            """
            inline operator bool() const { return ( d != 0 ); }
            ""","""
            bool operator bool () const;
            """)
        
    def testInline2(self):
        self.ioTest(
            """
inline bool TileId::operator==( TileId const& rhs ) const
{
    return m_zoomLevel == rhs.m_zoomLevel
        && m_tileX == rhs.m_tileX
        && m_tileY == rhs.m_tileY
        && m_mapThemeIdHash == rhs.m_mapThemeIdHash;
}""", """
bool TileId:: operator== (const TileId& rhs) const;
""")

    def testMacro(self):
        self.parser.bareMacros = ["Q_OBJECT"]
        self.ioTest(
            """
            class FooWidget : public QObject {
                    Q_OBJECT
                public:
                    FooWidget();
            };
            """,            """
            class FooWidget : QObject {
                    Q_OBJECT
                public:
                    FooWidget ();
            };
            """)

    def testMacro2(self):
        self.parser.bareMacros = ["FOO_EXPORT"]
        self.mirrorTest(
            """
            class FOO_EXPORT FooWidget {
            };
            """)

    def testMacro3(self):
        self.parser.macros = ["Q_DISABLE_COPY"]
        self.mirrorTest(
            """
            class FooWidget {
                public:
                    Foo ();
                private:
                    Q_DISABLE_COPY(FooWidget)
            };
            """)

    def testMacro4(self):
        self.parser.bareMacros = ["KGGZMOD_EXPORT"]
        self.mirrorTest(
            """
class Module
{
public:
    Module (const QString& name);
    ~Module ();

    enum State
    {
            created,
            done
    };
};
            """)

    def testBitfield(self):
        self.mirrorTest(
            """
            bool mHasMin : 1;
            """,debugLevel=0)

    def testAccess(self):
        self.mirrorTest(
            """void PlainPreFunc ();
class Foo {
    public:
        class Bar {
                void privateBar ();
        };
        void publicFoo ();
};
void PlainPostFunc ();
""")

    def testMacro4(self):
        self.parser.bareMacros = ["Q_OBJECT"]
        self.parser.macros = ["Q_PROPERTY"]
        self.ioTest(
            """
class AbstractRunner : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool matchingSuspended READ isMatchingSuspended WRITE suspendMatching NOTIFY matchingSuspend)
    Q_PROPERTY(QString id READ id);
};
""","""
class AbstractRunner : QObject
{
        Q_OBJECT
        Q_PROPERTY(bool matchingSuspended READ isMatchingSuspended WRITE suspendMatching NOTIFY matchingSuspend)
        Q_PROPERTY(QString id READ id)
};
""")

    def testFunnyNamespace(self):
        self.mirrorTest(
        """
class KJob;
namespace KIO
{
class Job;
};
class KAutoMountPrivate;
""")

    def testNestedTemplate(self):
        self.mirrorTest(
        """
KBookmarkGroup addBookmarks (const QList<QPair<QString,QString>>& list);
""")

    def testOperatorQUrlConst(self):
        self.ioTest(
        """
class Foo {
void reset( bool recursive = false );
operator QUrl() const { return uri(); }
bool operator==( const Entity& other ) const;
};
""","""
class Foo {
        void                    reset (bool recursive = false);
        QUrl                    operator QUrl () const;
        bool                    operator== (const Entity& other) const;
};
""")

    def testPureVirtualDestructor(self):
        self.mirrorTest(
        """
class Foo {
public:
    Foo ();
    virtual ~Foo ()=0;
};

""")

    def testComments(self):
        self.mirrorTest(
        """
class Foo {
    /**
     * bar docs.
     */
public:
    void bar ();
};

""")

    def testPrivateSignalHack(self):
        text = """
class KJob : public QObject
{
    Q_OBJECT
    Q_ENUMS( KillVerbosity Capability Unit )
    Q_FLAGS( Capabilities )

public:
       
public Q_SLOTS:
    bool suspend();
    
protected:
    virtual bool doKill();

public:
    bool exec();

Q_SIGNALS:
#ifndef Q_MOC_RUN
#ifndef DOXYGEN_SHOULD_SKIP_THIS
private: // don't tell moc or doxygen, but those signals are in fact private
#endif 
#endif
    void result(KJob *job);
};
"""
        self.parser.bareMacros = qtkdemacros.QtBareMacros()
        self.parser.macros = qtkdemacros.QtMacros()
        self.parser.preprocessorSubstitutionMacros = qtkdemacros.QtPreprocessSubstitutionMacros()
        scope = self.parser.parse(self.syms, text)
        #print(scope.format())


    #def testLiveAmmo(self):
    #    with open("/home/sbe/devel/svn/kde/trunk/KDE/kdelibs/kdecore/jobs/kjob.h") as fhandle:
    #        text = fhandle.read()
    #    self.parser.bareMacros = qtkdemacros.QtBareMacros(["KDECORE_EXPORT","KDE_EXPORT","KIO_EXPORT","KDE_DEPRECATED", "KDECORE_EXPORT_DEPRECATED"])
    #    self.parser.macros = qtkdemacros.QtMacros()
    #    self.parser.preprocessorSubstitutionMacros = qtkdemacros.QtPreprocessSubstitutionMacros()
    #    scope = self.parser.parse(self.syms, text)
    #    print(scope.format())

    def testFriendOperator(self):
        self.ioTest(
        """
class GeoDataLatLonAltBox : public GeoDataLatLonBox
{
friend bool operator == ( GeoDataLatLonAltBox const& lhs, GeoDataLatLonAltBox const& rhs);
};
""","""
class GeoDataLatLonAltBox : GeoDataLatLonBox
{
bool operator== (const GeoDataLatLonAltBox& lhs, const GeoDataLatLonAltBox& rhs);
};
""")

#     def testFriendOperator2(self):
#         self.parser.bareMacros = qtkdemacros.QtBareMacros(["KDECORE_EXPORT"])
#         self.mirrorTest("""
# class Foo {
#     static KDateTime realCurrentLocalDateTime();
#     friend QDataStream KDECORE_EXPORT &operator<<(QDataStream &out, const KDateTime &dateTime);
#     friend QDataStream KDECORE_EXPORT &operator>>(QDataStream &in, KDateTime &dateTime);
# };
# """)

if __name__ == '__main__':
    unittest.main()
