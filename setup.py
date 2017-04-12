#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2017 Endless Mobile, Inc.

import os
from setuptools import setup, find_packages

with open(os.path.join('hotdoc_modular_framework', 'VERSION.txt'), 'r') as _:
    VERSION = _.read().strip()

setup(name='hotdoc-modular-framework',
    version=VERSION, keywords="gjs modular-framework hotdoc",
    url='https://github.com/endlessm/hotdoc-modular-framework',
    author_email='philip@endlessm.com',
    license='LGPLv2.1+',
    description=('An extension for Hotdoc to generate documentation for '
        'the Endless modular framework for offline content'),
    author='Philip Chimento',
    packages=find_packages(),

    package_data={
        '': ['*.html'],
        'hotdoc_modular_framework': ['VERSION.txt'],
    },

    entry_points={
        'hotdoc.extensions': ('get_extension_classes = '
            'hotdoc_modular_framework.extension:get_extension_classes'),
    },
)
