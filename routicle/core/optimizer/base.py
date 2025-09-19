# -*- encoding: utf-8 -*-

"""
Base Class Defination of a Optimization Problem

The abstract base class are pydantic models which are defined to cater
the typical attributes and constraints for an optimization problem
like share of business optimization.
"""

import warnings

from abc import ABC, abstractmethod
from typing import Iterable, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

import pulp as p

from routicle.core.networkx import nxGraph
from routicle.components.base import PointOfInterest

class BaseOptimizerModel(BaseModel, ABC):
    model_config = ConfigDict(extra = "allow")

    name : str = Field(..., description = "Model Name")
    network : object = Field(..., description = "Routicle NetworkX")

    # define the sense, for minimization/maximization
    sense : int = Field(1, description = "Objective of the Problem")


    @property
    @abstractmethod
    def nvariables(self) -> Iterable:
        """
        Returns the Variables for the Optimization Problem
        """

        pass


    @property
    @abstractmethod
    def nconstraints(self) -> Iterable:
        """
        Returns the Constraints for the Optimization Problem
        """

        pass


    @abstractmethod
    def create_constraints(
        self, demandnodes : Iterable[PointOfInterest]
    ) -> Iterable:
        """
        Create the Constraints for the Optimization Problem

        Given a set of demand variable, automatically define the
        constraints by finding the connected nodes to the demand point.
        """

        pass


    @model_validator(mode = "after")
    def validate_sense(self) -> object:
        assert self.sense in [1, -1], "Undefined Model Sense"
        return self


    @model_validator(mode = "after")
    def validate_network(self) -> object:
        assert isinstance(self.network, nxGraph), "Incompitable Data"
        return self


    @abstractmethod
    def optimize(self, *args, **kwargs) -> None:
        """
        Abstract Method to Invoke Optimization using External Modules

        The :mod:`routicle` is designed to cater and provide wrapper
        for multiple extrnal modules, thus switching is provided with
        ease by providing an universal abstract function for control.
        """

        pass


class PuLPModel(BaseOptimizerModel, p.LpProblem):
    """
    The Class for Solving an LP (Linear Programming) Problem with PuLP

    :mod:`PuLP` is a robust python module for linear programming by
    defining a problem definition with various attributes and property
    to find a solution. The class is a subclass of :attr:`p.LpProblem`
    that integrates and wraps the functionalities over a the defined
    :mod:`networkx` graph with edges and nodes.

    The model is an instance of both ``BaseOptimizerModel`` and the
    ``p.LpProblem`` in the order of initialization preference. Thus,
    any method which is valid for ``p.LpProblem`` is also available;
    while the generalized function like :func:`.optimize()` is also
    available to the end users.

    :type  varname, lbattr, ubattr, varcategory: str
    :param varname, lbattr, ubattr, varcategory: The node property
        with which the ``p.LpVariable`` is initialized for ``[name,
        lowBound, upBound, cat]`` attribute respectively. The default
        values are the node attributes ``[cidx, minvalue, maxvalue,
        varcategory]`` which if not defined uses the default value as
        ``[<node.name>, 0.0, None, "Integer"]`` values.
    """

    varname : Optional[str] = Field(
        "cidx", description = "Name Field"
    )
    varcategory : Optional[str] = Field(
        "varcategory", description = "Field for Variable Category"
    )

    lbattr : Optional[str] = "minvalue"
    ubattr : Optional[str] = "maxvalue"

    def __init__(self, **data) -> None:
        BaseOptimizerModel.__init__(self, **data)
        p.LpProblem.__init__(self, self.name, sense = self._sense)

        # add the variables to the problem definition
        self += self.__define_objective__(), "Objective Function"


    @property
    def _sense(self) -> int:
        return p.LpMinimize if self.sense == -1 else p.LpMaximize


    @property
    def nvariables(self) -> Iterable[p.LpVariable]:
        """
        Return the LP Variables from the NetworkX Graph

        The ``nvariables`` for a :mod:`pulp` model is an iterable of
        :attr:`p.LpVariable` with a set of attributes defined from
        the network object. All the values ideally should be a property
        of the node, however if not defined defaults to ``LpVariable``
        values. In addition, the node attributes are mutated to not
        be null when setting bounds which is updated by :mod:`pulp`.
        """
        
        return self.variables()


    @property
    def nconstraints(self) -> dict:
        return self.constraints
    

    def create_constraints(
        self,
        demandnodes : Iterable[PointOfInterest],
        demandattrname : str = "demand"
    ) -> dict:
        """
        Create an Ierable of Constraints for the Demand Nodes
        """

        demand = {
            idx : {
                "object" : node,
                "demand" : dict(node)[demandattrname],
                "suppliers" : self.network.adjacent_nodes(
                    node.name, reverse = True
                )
            }
            for idx, node in enumerate(demandnodes)
        }

        supply = {
            idx : {
                "object" : self.network.dnodes[supplier],
                "demanders" : self.network.adjacent_nodes(
                    self.network.dnodes[supplier].name
                )
            }
            for idx, supplier in enumerate(list(set([
                supplier for suppliers in [
                    value["suppliers"] for value in demand.values()
                ]
                for supplier in suppliers
            ])))
        }

        iterables = list()
        for s in supply.values():
            iterable = [self.network.dedges[
                (s["object"].name, d)].cidx for d in s["demanders"]
            ]

            # the defined iterable is the edges name, get the varname
            # from the defined variables set and add constraint
            iterables.append({
                "object" : s["object"],
                "variables" : [
                    self.nvariables[pos]
                    for pos, varname in enumerate(self.nvariables)
                    if str(varname) in iterable
                ]
            })

        return demand, supply, iterables


    def optimize(self, *args, **kwargs) -> None:
        """
        A PuLP Optimization using Objective Function on a Graph
        """

        return self.solve()


    def __define_objective__(self) -> None:
        """
        Define Objective Function from the Defined Network Edges
        """

        edgevars = []
        for edge in self.network.G.edges:
            edge = self.network.inspect(edge, component = "edge")
            edgevars.append(edge.weight * p.LpVariable(edge.cidx))

        return p.lpSum(edgevars)


    def __reset_constraints__(
            self, keys : Iterable[str] = None
        ) -> None:
        """
        Reset all the Model Constraints
        """

        keys = keys or self.nconstraints.keys()

        for key in list(keys):
            if key in self.constraints:
                del self.constraints[key]
            else:
                warnings.warn(f"Key {key} not in Constraint")

        return None
