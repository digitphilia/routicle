# -*- encoding: utf-8 -*-

"""
Route (Optimzation) Miracles : Routicle Module

An inventory planning, stock routing and optimization library using
graph theory and shortest path detection algorithm like Dijkstra/A*
optimization using ``networkx`` and ``gravis`` for visualization.

The module encapsulates a problem statement by defining a graph, and
from the defined network any type of optimization and prediction can
be carried out. This approach ensures uniform approach and utility
functions are provided to provide a wrapper for external modules like
``pulp`` or ``ortools`` for supply chain optimizations.

@author: Debmalya Pramanik
@copywright: 2024; Debmalya Pramanik
"""

import os

# ? package follows https://peps.python.org/pep-0440/
# ? https://python-semver.readthedocs.io/en/latest/advanced/convert-pypi-to-semver.html
__version__ = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION"), "r").read()

# init-time options registrations
from routicle import utils # noqa: F401, F403
from routicle import components # noqa: F401, F403

# core components of routicle module
from routicle.core import networkx as nx # noqa: F401, F403
