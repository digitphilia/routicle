# -*- encoding: utf-8 -*-

"""
Base Class Defination of Graph Components

The abstract base class are pydantic models which are defined to cater
the typical attributes and constraints of a component - like a node
and an edge of a graph.
"""

from typing import Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, model_validator

class BaseComponent(BaseModel, ABC):
    """
    Abstract Base Validator Class for any Objective

    A base component is generic with any of the underlying environment
    which can be accepted by the module. Check ``environ`` for more
    details on setting up the environment for optimization.

    :ivar name: A name for the component object, which can be anything
        from ``label`` name in a :mod:`NetworkX` module or a variable
        name under a :mod:`PuLP` module, etc.

    :ivar cidx: An unique identity for the base component. It is
        recommended to create an identity with prefix "N" representing
        a node while an edge can be prefixed by "E" followed by any
        number of characters. When using a different type of solver,
        you can prefix with "V" for variable, or skip. One can also
        use an unique identity generator to define the name. Typically,
        the unique identification key should only be used by a
        developer or an adminitrator and must not be exposed to a
        third party application or an API call.

    :ivar environ: An unique identifier to modify or enable attributes
        based on the available environment. The environment can be any
        one of the supported modules for optimization and all the
        attributes and functions are modeled accordingly.

            * **nx** : An interface for the :mod:`networkx` module and
              all the modules are configured as :attr:`attribute` for
              easy integration.

            * **p.variable** : A type of :mod:`pulp` which is always
              of type ``p.LpVariable(...)`` object.

    Code Example(s)
    ---------------

    A component is defined such that any object is always an instance
    of the ``BaseComponent`` thus any object can be defined like:

    .. code-block:: python

        import routicle.components as components
        
        # let's define a graph component using networkx
        class GraphNode(components.base.BaseComponent):
            ...

            @property
            def environ(self) -> str:
                return "nx"

        node = GraphNode(name = "N001", ...)

        # a typical attributes like ``label`` or ``attributes`` are
        # made available through underlying properties explicit
        print(node.label)
        >> ... # this may be same as ``name`` or ``cidx``

    Any component has any defined constraints, requirements, etc. are
    always defined from base component objects, while an environment
    and related attributes should be modeled accordingly.
    """

    name : str = Field(..., description = "Name of the Component")
    cidx : Optional[str] = Field(..., description = "Unique Identity")

    # environment selection component, required
    environ : str = Field(..., description = f"Any of Accepted Value")


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


    @property
    def available_environ(self) -> tuple:
        """
        A Tuple of Valid Values for the Environment
        """

        return ("nx", "p.variable")


    @model_validator(mode = "after")
    def validate_environ(self) -> object:
        """
        Validate the Environment Attribute from a Valid Tuple
        """

        assert self.environ in self.available_environ, \
            f"Environment is Not Valid."
        
        return self


class GraphNode(GraphComponent):
    """
    Abstract Class Defination of a Node

    In graph theory, a node, also known as a "vertex", is a fundamental
    unitthat represents an entity or object within the graph. Nodes are
    connected to each other by edges, forming the structure of a graph.

    :ivar label: Display label of a node. The node label can be the
        same as the ``cidx`` i.e., the component identity key, or can
        be a custom one based on user preference. For any external
        applications one should always refer to the label attribute
        instead of the unique identity key.

    :ivar image: A custom icon is not supported directly by the ``nx``
        module, however once combined with ``gravis`` or ``matplotlib``
        this is possible by setting an attribute or native functions.
        The image is a typical attribute name for ``gravis`` module.

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
    image : Optional[str] = Field(
        "../assets/icons/graph.png",
        description = "Image Icon (png) for a Node"
    )

    # ? Minimum and Maximum Capacity of a Node
    mincapacity : float = 0.0
    maxcapacity : float = float("inf")


    @model_validator(mode = "after")
    def validate_capacity(self) -> object:
        """
        Assert if the Capacity are Justifiable
        """

        min_, max_ = self.mincapacity, self.maxcapacity
        assert min_ <= max_, \
            f"Min. Capacity ({min_:,.2f}) > Max. Capacity ({max_:,.2f})"
        
        return self


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

    :ivar unode, vnode: The nodes ``u`` and ``v`` between which an
        edge is connected. Follows the ``networkx`` nomenclature.

    :ivar label: The label of an edge in the graph. This is an
        optional value and can be anything - for example final weight,
        name of the edge etc. Child class may override the value as
        per need basis.
    """

    unode : object = Field(..., description = "Node at Edge `u`")
    vnode : object = Field(..., description = "Node at Edge `v`")
    label : Optional[str] = Field(None, description = "Display Label")

    # allow color to be edited from outside, set default as private
    _color = "#191A1C"


    @property
    def color(self) -> str:
        return self._color


    @property
    @abstractmethod
    def weight(self) -> float:
        """
        Weight of an Edge for Path Calculation

        An edge must always have an weight associated with it, which
        can be a combination of fields like cost, time, etc. For a
        graph which does not have an weight - there is no optimization
        possible and greedy search must always be avoided.
        """

        pass


    def __setattr__(self, name : str, value : Any) -> None:
        """
        Set/Override Attributes from Outside Scope of Class

        Allow only certain attributes to be overriden from outside the
        scope of the class variable. Warning: This is a destructive
        function, and thus only certain attributes are allowed to be
        changed. Currently, only allowed are ``["color"]`` attributes.

        Example Usage
        -------------

        The value of ``color`` attribute can be overwritten using the
        private variable ``_color`` which is the internal private
        attribute for the same.

        .. code-block:: python

            edge = GraphEdge(...)

            print(edge.color) # get default value
            >> #191A1C

            edge._color = "#2F56A5" # ⚠️ note private variable use
            print(edge.color) # get the update property value
            >> #2F56A5

            # or you can call the .__setattr__ method directly
            edge.__setattr__(name = "_color", value = "#2F56A5")
            >> ...

            edge.label = "new value" # ❌ not allowed
            >> ValueError ...

        The :mod:`pydantic` models are immutable ``Frozen = True`` by
        default, the private variable usage is used to override.
        """

        allowed = ["_color"] # only allow the defined

        if name not in allowed:
            raise ValueError(f"Attribute `{name}` is Immutable.")

        return object.__setattr__(self, name, value)
