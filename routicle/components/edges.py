# -*- encoding: utf-8 -*-

"""
Defination of a Edges Attributes for a Gaph
"""

from pydantic import ConfigDict

from routicle.components.base import POIConnector

class TimeEdge(POIConnector):
    """
    An Edge (connection b/w nodes) with a Time Parameter

    An edge where time is required to be minimized, is defined as a
    time based edge and typically for a supply chain problem this
    factor needs to be minimized.

    :ivar time: Time required for the transport, this is typically a
        factor which requires minimization.
    """

    time : float


    @property
    def weight(self) -> float:
        return self.time


    @property
    def attributes(self) -> dict:
        return dict(
            time = self.time,
            color = self.color,
            weight = self.weight
        )


class CostEdge(POIConnector):
    """
    An Edge (connection b/w nodes) with a Cost Parameter

    An edge where cost is required to be minimized, is defined as a
    cost based edge and typically for a supply chain problem this
    factor needs to be minimized.

    :ivar cost: The cost required, example inland freight, handling
        cost etc. for the transport. This is also typically requires a
        minimization approach.
    """

    cost : float


    @property
    def weight(self) -> float:
        return self.cost


    @property
    def attributes(self) -> dict:
        return dict(
            time = self.time,
            color = self.color,
            weight = self.weight
        )



class TimeCostEdge(POIConnector):
    """
    An Edge (connection b/w nodes) with a Time & Cost Parameter

    The two most common type of weights associated with a supply chain
    and logistics problem are (I) by when, and (II) at what cost. The
    model computes the weight based on these two factors.

    :ivar time: Time required for the transport, this is typically a
        factor which requires minimization.

    :ivar cost: The cost required, example inland freight, handling
        cost etc. for the transport. This is also typically requires a
        minimization approach.
    """

    model_config = ConfigDict(extra = "allow")

    time : float
    cost : float


    @property
    def weight(self) -> float:
        return self.time * self.cost


    @property
    def attributes(self) -> dict:
        return dict(
            cost = self.cost,
            time = self.time,
            color = self.color,
            weight = self.weight
        )
