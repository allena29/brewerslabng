#!/usr/bin/env python

from distutils.core import setup

setup(name='brewerslab',
      version='1.29',
      description='Brewerslab',
      author='Adam Allen',
      author_email='pybrwlab@brewerslab.mellon-collie.net',
      url='http://brewerslab.mellon-collie.net/python/',
      py_modules =['brewerslabEngine','brewerslabData','BJCPxmltools'],
     license="GPLv2+",
      classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Console',
       'License :: OSI Approved :: GNU General Public License (GPL)',
      'Intended Audience :: Developers',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries',
      ],
     )


