from setuptools import setup, find_packages
# pylint: disable=no-name-in-module,F0401,W0232,C0111,R0201


def readme():
    "Returns the contents of the README.rst file"
    with open("README.rst") as f:
        return f.read()


setup(
    name='libfutrli',
    version="0.2",
    description='Python3 library for uploading non-financial data to Futrli',
    long_description=readme(),
    author='Prairie Dog Brewing CANADA Inc',
    author_email='gerad@prairiedogbrewing.ca',
    url='https://github.com/geradcoles/libfutrli',
    packages=find_packages(),
    install_requires=[],
    scripts=[
        'bin/futrli',
    ],
    test_suite="nose.collector",
)
