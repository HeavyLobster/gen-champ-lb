#!/usr/bin/env python3

from setuptools import setup


setup(
    name='libchampmastery',
    version='0.1.0',
    description="A library for fetching League of Legends mastery data",
    license='LGPL-3.0',
    author='HeavyLobster',
    url='https://github.com/HeavyLobster/libchampmastery',
    py_modules=['libchampmastery'],
    install_requires=['requests>=2.18.4'],
    python_requires='>=3.5'
)
