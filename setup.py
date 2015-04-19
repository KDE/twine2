#!/usr/bin/python3

from distutils.core import setup
import kbindinggenerator

DESC = """Generate sip based Python bindings for C++ programs."""

setup(name='kbindinggenerator',
      version=kbindinggenerator.__version__,
      description=DESC,
      author='Simon Edwards',
      author_email='simon@simonzone.com',
      maintainer='Scott Kitterman',
      maintainer_email='scott@kitterman.com',
      url='https://projects.kde.org/projects/playground/bindings/twine2',
      license='GPL2/3+',
      py_modules=['kbindinggenerator'],
      keywords = ['KDE','sip','C++ bindings'],
      scripts = ['kf5.py','kdelibs.py', 'kdeedu.py'],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3i :: Only',
        'Programming Language :: C++',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ]
)
