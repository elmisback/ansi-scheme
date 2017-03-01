#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='ansi-scheme',
    description='set terminal colors on the fly',
    author='elmisback',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ansi-scheme = ansi_scheme.cli:cli'
        ]
      },
    package_data={
        'ansi_scheme': ['default-schemes/*.colors']
    }
)
