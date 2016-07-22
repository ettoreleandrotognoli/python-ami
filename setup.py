# -*- encoding: utf-8 -*-
__author__ = 'ettore'

import os

from setuptools import setup, find_packages

from asterisk import __version__


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


requirements = []
str_version = ".".join(map(str, __version__))

setup(
    name="asterisk-ami",
    version=str_version,
    description="Python AMI Client",
    long_description=read('README.rst'),
    url='https://github.com/ettoreleandrotognoli/python-ami/',
    download_url='https://github.com/ettoreleandrotognoli/python-ami/tree/%s/' % str_version,
    license='BSD',
    author=u'Éttore Leandro Tognoli',
    author_email='ettore.leandro.tognoli@gmail.com',
    packages=find_packages(exclude=['tests','examples']),
    include_package_data=True,
    keywords=['asterisk', 'ami'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    # install_requires=requirements,
    # tests_require=[],
)
