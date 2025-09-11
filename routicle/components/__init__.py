# -*- encoding: utf-8 -*-

"""
Defination of Graph Components - Nodes, Edges, etc.

The graph components with default attributes are defined under this
submodule. The components default attributes - for example for a node
weights, constraints, etc. are defined. All the components are
derived from the base class defined under ``base.py`` which is an
abstract pydantic validator class.
"""

from routicle.components import edges # noqa: F401, F403
from routicle.components import nodes # noqa: F401, F403
