# Copyright 2013-2018 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


# replace all 'x-y' with 'xY' (e.g. 'Py-morph-tool' -> 'PyMorphTool')
class PyBraynsCircuitStudioBackend(PythonPackage):
    """WebSocket server that acts as a personal backend for Circuit Studio client."""

    homepage = "https://bbpteam.epfl.ch/documentation/projects/brayns-circuit-studio-backend"
    git      = "git@bbpgitlab.epfl.ch:viz/brayns/braynscircuitstudiobackend.git"

    version('develop', branch='master')
    version('1.0.0', tag='brayns-circuit-studio-backend-v1.0.0')

    depends_on('py-setuptools', type='build')  # type=('build', 'run') if specifying entry points in 'setup.py'

    # for all 'foo>=X' in 'install_requires' and 'extra_requires':
    # depends_on('py-foo@<min>:')
