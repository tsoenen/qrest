"""The setuptools based setup module for rest-client.

Following the guidelines at:
https://packaging.python.org/en/latest/distributing.html

Used as a starting point:
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import re

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# Versions should comply with PEP440.  For a discussion on single-sourcing
# the version across setup.py and the project code, see
# https://packaging.python.org/en/latest/single_source_version.html
version = "0.0.0"
current_dir = path.dirname(__file__)
with open(path.join(current_dir, "qrest", "__init__.py")) as f:
    rx = re.compile('__version__ = "(.*)"')
    for line in f:
        m = rx.match(line)
        if m:
            version = m.group(1)
            break


# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    #    name='universal-rest-client',
    name="qrest",
    version=version,
    description="A generic python REST client",
    long_description=long_description,
    # The project's main homepage.
    url="https://bitbucket.org/nhm_bioinformatics/qrest/",
    # Author details
    author="Joris Benschop (BASF Vegetable Seeds)",
    author_email="joris.benschop@gmail.com",
    maintainer="Joris Benschop",
    maintainer_email="joris.benschop@gmail.com",
    # Choose your license
    license="GPLv3",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # What does your project relate to?
    keywords="generic REST API client",
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=["docs", "test"]),
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    # py_modules=["rest_client"],
    # qrest requires at least Python 3.6 (as it uses f-strings)
    python_requires="~=3.6",
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=["requests", "uritools", "jsonschema"],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={"dev": ["Sphinx"], "test": ["requests-mock"]},
)
