# -*- encoding: utf-8 -*-

"""
Route (Optimzation) Miracles : Routicle Module

An inventory planning, stock routing and optimization library using
graph theory and shortest path detection algorithm like Dijkstra/A*
optimization using ``networkx`` and ``gravis`` for visualization.

@author: Debmalya Pramanik
@copywright: 2024; Debmalya Pramanik
"""

import os

# ? package follows https://peps.python.org/pep-0440/
# ? https://python-semver.readthedocs.io/en/latest/advanced/convert-pypi-to-semver.html
__version__ = open(os.path.join(os.path.abspath(__file__), "VERSION"), "r").read()

# init-time options registrations
