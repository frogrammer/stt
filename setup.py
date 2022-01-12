from setuptools import setup, find_packages
from os import path

from app import __version__

# https://packaging.python.org/guides/making-a-pypi-friendly-readme/
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='databricks-workspace-tool',
    version=__version__,
    description='Tool to manage notebooks and clean output cells.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/frogrammer/databricks-workspace-tool',
    author='Luke Vinton',
    author_email='luke0vinton@gmail.com',
    license='Apache 2.0',
    packages=find_packages(),
    install_requires=['fire', 'databricks-cli', 'fire-cli-helper', 'gitpython'],
    tests_require=[],
    classifiers=[],
    test_suite='',
    entry_points={
        'console_scripts': [
            'dwt = cli.__main__:main',
        ],
    },
)