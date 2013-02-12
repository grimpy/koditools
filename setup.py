#!/usr/bin/env python2
from distutils.core import setup

setup(name='xbmctools',
      version='0.1',
      description='Python remote tools for XBMC',
      author='Jo De Boeck',
      author_email='deboeck.jo@gmail.com',
      url='http://github.com/grimpy/xbmctools',
      packages=['xbmctools'] ,
      scripts=['xbmcremote', 'xbmcpidgin'],
     )
