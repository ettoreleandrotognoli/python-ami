# -*- encoding: utf-8 -*-
__author__ = 'ettore'

import os

from setuptools import setup, find_packages

from asterisk import __version__


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


requirements = []

setup(
    name="My App",
    version=".".join(map(str, __version__)),
    description="Python AMI Client",
    long_description=read('README.rst'),
    url='http://programandonoaquario.com.br',
    license='UNDEFINDED',
    author=u'Éttore Leandro Tognoli',
    author_email='ettore.leandro.tognoli@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=requirements,
    tests_require=[],
)
