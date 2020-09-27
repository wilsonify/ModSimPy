from distutils.core import setup


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name='modsimpy',
    version='1.1.3',
    packages=['modsim'],
    url='http://github.com/wilsonify/ModSimPy',
    license='LICENSE',
    description='Python library for the book Modeling and Simulation in Python.',
    long_description=readme(),
)
