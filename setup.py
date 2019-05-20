from setuptools import setup, find_packages

setup(
    name             = 'conclave-data',
    version          = '0.0.0.1',
    packages         = find_packages(),
    license          = 'MIT',
    url              = 'https://github.com/cici-conclave/conclave-data',
    description      = 'Utilities for handling data from remote object stores.',
    long_description = open('README.md').read()
)