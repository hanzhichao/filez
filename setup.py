#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""
import os
from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))
setup_requirements = []
version = '0.14'

def read_file(filename):
    with open(os.path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


setup(
    author="Han Zhichao",
    author_email='superhin@126.com',
    description='Easy use for fetch data from kinds of files',
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
    license="MIT license",
    include_package_data=True,
    keywords=[
        'filez', 'email', 'attachments',
    ],
    name='filez',
    packages=find_packages(include=['filez']),
    setup_requires=setup_requirements,
    url='https://github.com/hanzhichao/filez',
    version=version,
    zip_safe=True,
    install_requires=[]
)
