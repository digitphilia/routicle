# -*- encoding: utf-8 -*-

"""
Defination of a Node Attributes for a Gaph

A node for supply chain and logistics problem is subclassified into
multiple types based on requirement. The definaion and attributes are
defined. The attributes are typical constraints like supply/demand for
a particular node type, for example a plant or an warehouse.
"""

from routicle.components.base import GraphNode

class NTPorts(GraphNode):
    """
    Node Type:: Port - A Location for Incoming Material

    A node (sea, air, rail, etc.) is a dedicated location of material
    import and/or export. Typically, a vendor can dump material at a
    port and based on inland charges the material can then be
    transported to/from another location.
    """

    @property
    def color(self) -> str:
        return "#FDE725"


class NTWarehouses(GraphNode):
    """
    Node Type:: Warehouses - A Location typically for Storage

    A warehouse is a location for storing raw materials and/or finished
    goods. An warehouse can have many constraints like some materials
    cannot be stored together. Currently, the model is kept simple
    with only capacity constraint however other attributes maybe added
    in a future version.
    """

    @property
    def color(self) -> str:
        return "#5EC962"


class NTPlants(GraphNode):
    """
    Node Type:: Plants - A Location for Manufaturing

    A plant is a location of manufacturing. In addition to storage
    capacity a plant must have a production constraint.

    :ivar rate: Production rate, which should be in the same unit as
        that of the capacity, per day.

    :ivar demand: Demand of a plant, typically for scheduling or for
        an inventory management problem.
    """

    rate : float
    demand : float

    @property
    def color(self) -> str:
        return "#3B528B"


class NTVendors(GraphNode):
    """
    Node Type:: Vendors - An Entity who can Supply Material

    A vendor can supply material to a location (ports, plants, etc.).
    A vendor's lead time is most of the route specific so this must be
    defined as a weight (``edges`` attributes).
    """

    @property
    def color(self) -> str:
        return "#440154"
