# -*- encoding: utf-8 -*-

"""
Defination of a Node Attributes ("Point of Interest") for a Gaph

A node for supply chain and logistics problem is subclassified into
multiple types based on requirement. The definaion and attributes are
defined. The attributes are typical constraints like supply/demand for
a particular node type, for example a plant or an warehouse.
"""

from typing import Optional
from pydantic import Field, ConfigDict

from routicle.components.base import PointOfInterest

class StorageUnits(PointOfInterest):
    """
    A Storage Unit is a Location of Storage, Base Class with Defaults

    A storage unit can be any storage locations; like ports,
    warehouses, etc. and typically has an constraint around capacity
    which is the default attribute of the base :class:`PointOfInterest`
    as already defined. The storage location class can accept any
    attributes which may be helpful in further development.

    This type of node (when ``u``) often requires a time and a cost
    for storage and transfer from and to one location to another. Check
    :class:`TimeCostEdge` for more information.

    Usage Example(s)
    ----------------

    A storage unit may have certain additional attributes defined to
    further enhance the model like:

    .. code-block:: python

        storage = StorageUnits(storageCost = XX)
        print(storage.storageCost)
        >> XX

    However, this is currently not in the scope of development and may
    be refined externally.
    """

    model_config = ConfigDict(extra = "allow")

    image : Optional[str] = Field(
        "../assets/icons/warehouse.png",
        description = "Image Icon (png) for a Node:: Storage Location"
    )

    @property
    def color(self) -> str:
        return "#FDE725"


class ManufacturingUnits(PointOfInterest):
    """
    Node Type:: Plants - A Location for Manufaturing

    A location for manufacturing, turning raw materials into finished
    goods. Each type of manufacturing point typically has a rate at
    which production is done and a demand, i.e., requirement.

    :ivar rate: Production rate, which should be in the same unit as
        that of the capacity, per day.

    :ivar demand: Demand of a plant, typically for scheduling or for
        an inventory management problem.

    In addition, any type of additional attributes are allowed to be
    passed for further calculations and enhancements.
    """

    model_config = ConfigDict(extra = "allow")

    image : Optional[str] = Field(
        "../assets/icons/conveyor.png",
        description = "Image Icon (png) for a Node:: PLANT"
    )

    rate : float
    demand : float

    @property
    def color(self) -> str:
        return "#3B528B"


class SupplyPoints(PointOfInterest):
    """
    Node Type:: Supply Points - An Entity who can Supply Material

    A supply point (a vendor, trader, etc.) who supply raw materials
    to a manufacturing unit for conversion or may supply finished goods
    (P2P materials) to delivery locations for selling.

    :ivar reliability: A weightage ∈ [0, 1] to determine efficiency of
        a supplying point in terms of historic performance. A score
        should be supplied, defaults to 1.0 (maximum) value.

    In addition, any type of additional attributes are allowed to be
    passed for further calculations and enhancements.
    """

    model_config = ConfigDict(extra = "allow")

    image : Optional[str] = Field(
        "../assets/icons/vendor.png",
        description = "Image Icon (png) for a Node:: VENDOR"
    )

    reliability : Optional[float] = Field(
        1.0,
        description = "Reliability Score ∈ [0.0, 1.0]"
    )

    @property
    def color(self) -> str:
        return "#440154"
