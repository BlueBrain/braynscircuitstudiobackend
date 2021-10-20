#!/usr/bin/env python

import importlib.util
import sys

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported")

# read the contents of the README file
with open("README.rst", encoding="utf-8") as f:
    README = f.read()

spec = importlib.util.spec_from_file_location(
    "brayns_circuit_studio_backend.version",
    "brayns_circuit_studio_backend/version.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VERSION = module.__version__

setup(
    name="brayns-circuit-studio-backend",
    author="BlueBrain Viz Team",
    author_email="bbp-ou-visualization@groupes.epfl.ch",
    version=VERSION,
    description="WebSocket server that acts as a personal backend for Circuit Studio client.",
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://bbpteam.epfl.ch/documentation/projects/brayns-circuit-studio-backend",
    project_urls={
        "Tracker": "https://bbpteam.epfl.ch/project/issues/projects/BCSB/issues",
        "Source": "git@bbpgitlab.epfl.ch:viz/brayns/braynscircuitstudiobackend.git",
    },
    license="BBP-internal-confidential",
    install_requires=[],
    packages=find_packages(),
    python_requires=">=3.6",
    extras_require={"docs": ["sphinx", "sphinx-bluebrain-theme"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)
