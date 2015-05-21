#!/usr/bin/env python2
from distutils.core import setup

setup(name='koditools',
      version='0.1',
      description='Python remote tools for Kodi',
      author='Jo De Boeck',
      author_email='deboeck.jo@gmail.com',
      url='http://github.com/grimpy/koditools',
      packages=['koditools'] ,
      package_dir={'koditools': 'koditools'},
      package_data={'koditools': ['templates/*']},
      scripts=['kodiremote', 'kodipidgin', 'kodisendto'],
     )
