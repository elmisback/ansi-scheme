#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='ansi-theme',
    description='set terminal colors on the fly',
    author='elmisback',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ansi-theme = ansi_theme:cli'
        ]
      },
    package_data={
        'ansi_theme': ['default-themes/*.colors']
    }
)
