#!/usr/bin/env python
# encoding: utf-8
from __future__ import absolute_import, print_function
from setuptools import setup, find_packages
import os
import tornado_xmlrpc


REQUIREMENTS = (
    'tornado>=4.1',
    'lxml',
    'slimurl',
)


if tornado_xmlrpc.PY2:
    REQUIREMENTS += ('futures',)


def walker(base, *paths):
    file_list = set([])
    cur_dir = os.path.abspath(os.curdir)

    os.chdir(base)
    try:
        for path in paths:
            for dname, dirs, files in os.walk(path):
                for f in files:
                    file_list.add(os.path.join(dname, f))
    finally:
        os.chdir(cur_dir)

    return list(file_list)


setup(
    name='tornado-xmlrpc',
    version=tornado_xmlrpc.__version__,
    author=tornado_xmlrpc.__author__,
    license="MIT",
    description="Tornado XML-RPC server and client",
    long_description=open('README.rst').read(),
    platforms="all",
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    include_package_data=True,
    zip_safe=False,
    package_data={
        'tornado_xmlrpc': ['xmlrpc.xsd'],
    },
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIREMENTS,
)
