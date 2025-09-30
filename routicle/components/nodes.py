# -*- encoding: utf-8 -*-

"""
Defination of a Node Attributes ("Point of Interest") for a Gaph

A node for supply chain and logistics problem is subclassified into
multiple types based on requirement. The definaion and attributes are
defined. The attributes are typical constraints like supply/demand for
a particular node type, for example a plant or an warehouse.
"""

import warnings

from typing import Optional
from pydantic import Field, ConfigDict, model_validator

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

    :type  available: float
    :param available: Available quantity at the storage location, this
        can be any float value and necessary objective may be defined
        to satisfy the minimum demand at the storage location, else in
        case of excess STO can be done.

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

    available : float = Field(
        0.0, description = "Available Capacity at Storage"
    )

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

    :ivar moq: Minimum order quantity for a supplier, which is the
        value that must be given if placing an order else 0. The value
        defaults to 0. The constrained is a parallel logic as below:
        ``OR(quantity = 0, quantity >= moq)`` for the supplier.

    :ivar packsize: A pack size of the supplier, which is a multiple
        value (typically for material dispatched in a bag, tanker,
        etc.). The value must be an multiple of :attr:`moq` else an
        warning is raised and the solution might be infeasible.

    :ivar reliability: A weightage ∈ [0, 1] to determine efficiency of
        a supplying point in terms of historic performance. A score
        should be supplied, defaults to 1.0 (maximum) value.

    :ivar minorder: Typically for a strategic supplier, a quantity
        must be given to the vendor. This is an optional control, which
        also reduces the risk of single source issue. Defaults to 0,
        unconstrined (this is different from MOQ).

    In addition, any type of additional attributes are allowed to be
    passed for further calculations and enhancements.
    """

    model_config = ConfigDict(extra = "allow")

    image : Optional[str] = Field(
        "../assets/icons/vendor.png",
        description = "Image Icon (png) for a Node:: VENDOR"
    )

    moq : float = Field(0.0, description = "Minimum Order Quantity")
    packsize : float = Field(1.0, description = "Pack Size of Supplier")

    reliability : Optional[float] = Field(
        1.0,
        description = "Reliability Score ∈ [0.0, 1.0]"
    )

    minorder : Optional[float] = Field(
        0.0,
        description = "A Value that Must be Assigned to the Supplier"
    )

    @property
    def color(self) -> str:
        return "#440154"


    @model_validator(mode = "after")
    def validate_config(self) -> object:
        """
        Assert/Raise Warning for the Configuration of the Supply Point

        Validate the configuration of the supplying points (nodes) for
        each, as below:

            1. A supply point cannot have a zero pack size, default
              multiple is one, which must be provided else an assertion
              error is raised.

            2. If MOQ is defined, then minimum order must be greater
              than or equal to MOQ value, else an infeasible solution
              will always be created.

        In addition to the assertion checks, the function also raises
        the following warnings:

            1. Minimum capacity of a supply point typically does not
              have any meaning, thus an warning is raised.

            2. Pack size must be a multiple of MOQ, else an warning is
              raised. This might give an infeasible solution, or to
              satisfy the demand, a vendor may be given more quantity
              just to find and meet the pack size constraint.
        """

        selfname = f"ON OBJECT :: {self.name}" # verbose
        mincapacity = self.mincapacity # from parent class
        moq, ps, mo = self.moq, self.packsize, self.minorder

        assert ps > 0.0, \
            f"{selfname} - Pack Size <= 0.0, Not Possible"

        if moq % ps != 0:
            warnings.warn("Pack Size is not a Multiple of MOQ")

        if mincapacity > 0.0:
            warnings.warn("Min. Capacity is defined at Supply Point")

        if mo > 0.0 and moq > 0.0 and mo < moq:
            warnings.warn(
                f"Possible Conflict b/w MOQ (= {moq}); defined, but" \
                + f" Min. Order Value (= {mo}) is a Lower Value. " \
                + f"i.e., Constraint is $(x >= {moq}) & (x >= {mo})$"
            )

        return self
