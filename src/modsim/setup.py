from distutils.core import setup
from setuptools import find_packages


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name='modsim',
    version='1.1.3',
    packages=find_packages(),
    url='http://github.com/wilsonify/ModSimPy',
    license='LICENSE',
    description='Python library for the book Modeling and Simulation in Python.',
    long_description=readme(),
)
