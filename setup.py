#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, print_function
from setuptools import setup, find_packages
import aiohttp_xmlrpc as module


setup(
    name=module.__name__.replace("_", "-"),
    version=module.__version__,
    author=module.__author__,
    license=module.__license__,
    description=module.description,
    long_description=open('README.rst').read(),
    platforms="all",
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    include_package_data=True,
    zip_safe=False,
    package_data={
        module.__name__: ['xmlrpc.rng'],
    },
    packages=find_packages(exclude=('tests',)),
    install_requires=(
        'aiohttp',
        'lxml',
    ),
    extras_require={
        'develop': [
            'pytest',
            'pytest-cov',
            'xmltodict',

        ],
    }
)
