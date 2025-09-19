# -*- encoding: utf-8 -*-

"""
Base Class Defination of a Optimization Problem

The abstract base class are pydantic models which are defined to cater
the typical attributes and constraints for an optimization problem
like share of business optimization.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

import pulp as p

from routicle.core.networkx import nxGraph

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

    :type  varname, lb, ub, varcategory: str
    :param varname, lb, ub, varcategory: The node property with which
        the ``p.LpVariable`` is initialized for ``[name, lowBound,
        upBound, cat]`` attribute respectively. The default values
        are the node attributes ``[cidx, mincapacity, maxcapacity,
        varcategory]`` which if not defined uses the ``p.LpVariable``.
    """

    varname : Optional[str] = Field(
        "cidx", description = "Name Field"
    )
    varcategory : Optional[str] = Field(
        "varcategory", description = "Field for Variable Category"
    )
    
    lb : Optional[str] = "mincapacity"
    ub : Optional[str] = "maxcapacity"

    def __init__(self, **data) -> None:
        BaseOptimizerModel.__init__(self, **data)
        p.LpProblem.__init__(self, self.name, sense = self._sense)

        # add the variables to the problem definition
        p.LpProblem.addVariables(self, self.nvariables)
        self += self.__define_objective__(), "Objective Function"


    @property
    def _sense(self) -> int:
        return p.LpMinimize if self.sense == -1 else p.LpMaximize


    @property
    def nvariables(self) -> Iterable[p.LpVariable]:
        """
        Get and Create LP Variables from the NetworkX Graph

        The ``nvariables`` for a :mod:`pulp` model is an iterable of
        :attr:`p.LpVariable` with a set of attributes defined from
        the network object. All the values ideally should be a property
        of the node, however if not defined defaults to ``LpVariable``
        values. In addition, the node attributes are mutated to not
        be null when setting bounds which is updated by :mod:`pulp`.
        """

        rvalue = []
        for node in self.network.G.nodes:
            node = dict(self.network.inspect(node))

            # mutate infinity values to None, controlled by pulp
            lb, ub = node.get(self.lb, None), node.get(self.ub, None)
            lb, ub = list(map(
                lambda x : None if x in [float("inf"), float("-inf")]
                else x, [lb, ub]
            ))

            rvalue.append(p.LpVariable(
                name = node.get(self.varname, node["name"]),
                lowBound = lb, upBound = ub,
                cat = node.get(self.varcategory, "Continuous")
            ))

        return rvalue


    @property
    def nconstraints(self) -> Iterable:
        return None


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
