# -*- encoding: utf-8 -*-

"""
Base Class Defination of Graph Components

The abstract base class are pydantic models which are defined to cater
the typical attributes and constraints of a component - like a node
and an edge of a graph.
"""

from typing import Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

class GraphComponent(BaseModel, ABC):
    """
    Abstract Base Class for a Graph Component

    The abstract base class of a graph component is inherited by all
    the models - nodes and edges. The component defines the attributes
    which is common and defines dunder methods which can be used to
    print the attributes to console (typically for logging).

    :ivar cidx: An unique identity for the graph component. It is
        recommended to create an identity with prefix "N" representing
        a node while an edge can be prefixed by "E" followed by any
        number of characters. One can also use an unique identity
        generator to define the name.
    """

    cidx : Optional[str] = Field(..., description = "Unique Identity")


    @property
    @abstractmethod
    def color(self) -> str:
        """
        Define Color (for HTML/front end) for a Graph Component

        We've used ``networkx`` and ``gravis`` to plot the graph for
        visualization. This is an optional property whose default value
        must be set in the ``node`` and ``edge`` component and can be
        extended to other child classes overriding the value.
        """

        pass


class GraphNode(GraphComponent):
    """
    Abstract Class Defination of a Node

    In graph theory, a node, also known as a "vertex", is a fundamental
    unitthat represents an entity or object within the graph. Nodes are
    connected to each other by edges, forming the structure of a graph.

    :ivar label: Display label of a node. The node label can be the
        same as the ``cidx`` i.e., the component identity key, or can
        be a custom one based on user preference.

    :ivar mincapacity: The minimum capacity of a node. Typically, any
        supply chain and logistics entity has a capacity associated
        with it - for example plants, warehouses, etc. The minimum
        capacity can be derived from additional models for maintenance
        of norms or minimum stock.

    :ivar maxcapacity: The maximum capacity of an entity, defaults to
        infinity.
    
    **Note:** The capacity should always be in a standard unit or the
    same should be maintained throughout.
    """

    label : Optional[str] = Field(None, description = "Display Label")

    # ? Minimum and Maximum Capacity of a Node
    mincapacity : float = 0.0
    maxcapacity : float = float("inf")


    def __init__(self, **attributes) -> None:
        attributes["label"] = attributes.get(
            "label",
            attributes["cidx"]
        )

        super().__init__(**attributes)


    @property
    def color(self) -> str:
        return "#42B3E3"


    @property
    def attributes(self) -> dict:
        return {
            k : v for k, v in vars(self).items()
            if k not in ["cidx", "label"] # discarded keys
        }


class GraphEdge(GraphComponent):
    """
    Abstract Class Defination of a Edge

    An edge, in Graph Theory, is a fundamental component which connects
    two vertices (or "nodes") of a graph. A edge can be directional or
    non-directional and have constraints (for e.g. cost, time, etc.)
    associated with it.

    :ivar label: The label of an edge in the graph. This is an
        optional value and can be anything - for example final weight,
        name of the edge etc. Child class may override the value as
        per need basis.
    """

    label : Optional[str] = Field(None, description = "Display Label")


    @property
    def color(self) -> str:
        return "#191A1C"
