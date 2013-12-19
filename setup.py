#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages

setup(name="transloadit",
      version="0.0.2",
      description="Library for interfacing with Transloadit's API",
      author="Joe Stump",
      author_email="calvin@edtwist.com",
      url="http://github.com/calvinalvin/python-transloadit",
      packages = find_packages(),
      license = "MIT License",
      install_requires=['simplejson>=2.1.6'],
      keywords="transloadit",
      zip_safe = True,
      tests_require=['nose', 'coverage'])
