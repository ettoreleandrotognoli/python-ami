# -*- encoding: utf-8 -*-
import os

from setuptools import setup, find_packages

__version__ = '0.2.devSNAPSHOT'
__revision__ = 'REVISION'

def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()

setup(
    name='asterisk-ami',
    version=__version__,
    description='Python AMI Client',
    long_description=read('README.rst'),
    url='https://github.com/ettoreleandrotognoli/python-ami/',
    download_url='https://github.com/ettoreleandrotognoli/python-ami/tree/%s/' % __revision__,
    license='BSD',
    author=u'Éttore Leandro Tognoli',
    author_email='ettore.leandro.tognoli@gmail.com',
    data_files=['requirements.txt'],
    packages=find_packages(
        './src/main/python/',
    ),
    package_dir={'': 'src/main/python'},
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
    install_requires=[

    ],
    tests_require=[
        "rx==1.6",
        "coverage",
        "twine",
        "autopep8",
    ],
)
