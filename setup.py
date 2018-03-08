#!/usr/bin/env python

from setuptools import setup


# Modified from http://stackoverflow.com/questions/2058802/
# how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
def version():
    import os
    import re

    init = os.path.join('beast2xml', '__init__.py')
    with open(init) as fp:
        initData = fp.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]+)['\"]",
                      initData, re.M)
    if match:
        return match.group(1)
    else:
        raise RuntimeError('Unable to find version string in %r.' % init)


setup(name='beast2-xml',
      version=version(),
      packages=['beast2xml'],
      package_data={'beast2xml': ['templates/*.xml']},
      url='https://github.com/acorg/beast2-xml',
      download_url='https://github.com/acorg/beast2-xml',
      author='Terry Jones',
      author_email='tcj25@cam.ac.uk',
      keywords=['BEAST2', 'XML'],
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      description=('Command line script and Python class for generating '
                   'BEAST2 XML config files.'),
      long_description=(
          'Please see https://github.com/acorg/beast2-xml for details.'),
      license='MIT',
      scripts=['bin/beast2-xml.py', 'bin/beast2-xml-version.py'],
      install_requires=['dark-matter>=1.1.28'])
