#!/usr/bin/env python

import importlib.util
import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 9):
    sys.exit("Sorry, Python < 3.9 is not supported")

spec = importlib.util.spec_from_file_location(
    "braynscircuitstudiobackend.version",
    "src/version.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.__version__

setup(
    name="braynscircuitstudiobackend",
    author="BlueBrain Viz Team",
    author_email="bbp-ou-visualization@groupes.epfl.ch",
    version=VERSION,
    description="Backend service for Brayns Circuit Studio software",
    long_description="",
    long_description_content_type="text/x-rst",
    url="https://bbpteam.epfl.ch/documentation/projects/braynscircuitstudiobackend",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/BCSB/issues",
        "Source": "git@bbpgitlab.epfl.ch:viz/brayns/braynscircuitstudiobackend.git",
    },
    license="BBP-internal-confidential",
    install_requires=[],
    packages=find_packages(),
    package_dir={
        "backend": "src/backend",
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
VERSION = module.__version__
