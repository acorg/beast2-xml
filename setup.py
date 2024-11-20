#!/usr/bin/env python

from setuptools import setup


setup(
    name="beast2-xml",
    version="1.3.0",
    packages=["beast2xml"],
    package_data={"beast2xml": ["templates/*.xml"]},
    url="https://github.com/acorg/beast2-xml",
    download_url="https://github.com/acorg/beast2-xml",
    author="Terry Jonesl",
    author_email="tcj25@cam.ac.uk",
    keywords=["BEAST2", "XML"],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description=(
        "Command line script and Python class for generating "
        "BEAST2 XML config files."
    ),
    long_description=("Please see https://github.com/acorg/beast2-xml for details."),
    license="MIT",
    scripts=["bin/beast2-xml.py", "bin/beast2-xml-version.py"],
    install_requires=[
        "dark-matter>=1.1.28",
        "pandas>=2.2.2",
        "ete3>= 3.1.3",
        "six>=1.16.0",
    ],
)
