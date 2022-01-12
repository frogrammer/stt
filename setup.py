from setuptools import setup, find_packages
from os import path

from . import src

# https://packaging.python.org/guides/making-a-pypi-friendly-readme/
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='stt',
    version=src.__version__,
    description='Tool to manage notebooks and clean output cells.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/frogrammer/stt',
    author='Luke Vinton',
    author_email='luvinton@microsoft.com',
    license='unlicense',
    packages=find_packages(),
    install_requires=[],
    tests_require=[],
    classifiers=[],
    test_suite='',
    entry_points={
        'console_scripts': [
            'stt = src.__main__:main',
        ],
    },
)