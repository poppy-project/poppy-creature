#!/usr/bin/env python

import re
import sys

from setuptools import setup, find_packages


def version():
    with open('poppy/creatures/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='poppy-creature',
      version=version(),
      packages=find_packages(),

      install_requires=['pypot>=3.0.0'],

      include_package_data=True,
      exclude_package_data={'': ['README.md', '.gitignore']},

      zip_safe=False,

      author='See https://github.com/poppy-project/pypot/graphs/contributors',
      author_email='pierre.rouanet@gmail.com',
      description='Abstract Poppy Creature Software Library',
      url='https://github.com/poppy-project/poppy-creature',
      license='GNU GENERAL PUBLIC LICENSE Version 3',

      **extra
      )
