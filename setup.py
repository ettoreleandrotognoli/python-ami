# -*- encoding: utf-8 -*-
import os

from setuptools import setup, find_packages

from asterisk import __version__


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


requirements = read('requirements.txt').splitlines()
str_version = '.'.join(map(str, __version__))

setup(
    name='asterisk-ami',
    version=str_version,
    description='Python AMI Client',
    long_description=read('README.rst'),
    url='https://github.com/ettoreleandrotognoli/python-ami/',
    download_url='https://github.com/ettoreleandrotognoli/python-ami/tree/%s/' % str_version,
    license='BSD',
    author=u'Éttore Leandro Tognoli',
    author_email='ettore.leandro.tognoli@gmail.com',
    data_files=['requirements.txt'],
    packages=find_packages(exclude=['tests', 'examples']),
    include_package_data=True,
    keywords=['asterisk', 'ami'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=filter(None, requirements),
    # tests_require=[],
)
