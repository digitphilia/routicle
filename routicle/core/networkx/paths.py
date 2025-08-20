# -*- encoding: utf-8 -*-

"""
A Set of Computations based on Paths of a NetworkX Graph
"""

from math import prod
from itertools import pairwise
from typing import Dict, Tuple, Iterable, Callable

import networkx as nx

from routicle.core.networkx.base import nxGraph
from routicle.components.base import GraphNode, GraphEdge

class PathAnalysis(nxGraph):
    """
    Analyse a Complete Graph Path from Source to Target

    Analyse source and target nodes and trace paths, weights, etc.
    which are availble as an attribute. The internal functions are
    heavily dependent on the :mod:`networkx` module and typically
    returns an interable of paths for further analysis.

    :ivar source, target: Source and target node label or the node
        object of :mod:`routicle.components.base.GraphNode` instance.
        Both the values cannot be None, and analysis is done on the
        available nodes.

    Note: Simple wrapper of :mod:`networkx` module are not available,
    and it is recommended to directly use those functions unless the
    functions are required multiple times in forward logics.

    .. code-block:: python

        import networkx as nx
        import routicle.core.networkx as rnx

        # create a model for path analysis from graph
        # source and target can be label or GraphNode instances
        model = PathAnalysis(
            G = G, dnodes = dnodes, dedges = dedges,
            source = "V1", target = dnodes["P4"]
        )

        # check if path exists between source to target
        print(nx.has_path(
            model.G, source = model.source, target = model.target
        ))
        >> True # or False, if path does not exists

    Some alternative inbuilt functions are modified and outputs are
    formatted for easy integration in forward models.
    """

    def __init__(
        self,
        G : nx.Graph,
        dnodes : Dict[str, GraphNode],
        dedges : Dict[Tuple[str, str], GraphEdge],
        source : GraphNode | str = None,
        target : GraphEdge | str = None
    ) -> None:
        super().__init__(G = G, dnodes = dnodes, dedges = dedges)
        self.source, self.target = self.__set_path__(source, target)


    def getpaths(
        self,
        rtype : str = "complete",
        attribute : str = "weight",
        calculate : str = "multiplicative",
        nxcostfunc : Callable = nx.dijkstra_path_length
    ) -> Iterable:
        """
        Check & Return All Simple Paths b/w Source and Target Node

        Calculate and find all the paths from source to target and
        returns an iterable of either edges or nodes.

        :type  rtype: str
        :param rtype: Choose to return a list of nodes or edges from
            all available paths from source to target. Allowed values
            are ``nodes``, ``edges`` and ``complete`` (default) only.

        :type  attribute: str
        :param attribute: The attribute name for calculation of weight
            from the path edges. Default attribute is "weight", check
            :attr:`routicle.components.edges.TimeCostEdge.weight` for
            more information on attributes definations.
        
        :type  calculate: str
        :param calculate: For a given path, the attribute can either
            be "additive" or "multiplicative" (default) to get the
            total weight of the augmented path.

        :type  nxcostfunc: function
        :param nxcostfunc: A :mod:`networkx` cost calculation function
            for an edge, defaults to :func:`nx.dijkstra_path_length`
            function which takes :attr:`attribute` as weight value.
            When the :attr:`calculate` is "additive" then value of
            weight and costs are always same.

        The :attr:`rtype` argument is versatile in formatting the
        output into any one of the desired format. The iterable has
        the following informations.

        .. code-block:: python

            ...
            print(model.getpaths(rtype = "nodes"))
            >> {
                "paths" : {
                    # "nodes" available for "nodes" and "complete"
                    "nodes" : [
                        [source, target],
                        ...,
                        [source, <node>, ..., target]
                    ],

                    # "edges" available for "edges" and "complete"
                    "edges" : [
                        [(source, target)],
                        ...,
                        [
                            (source, <node>),
                            (<node>, ...),
                            (..., target)
                        ]
                    ],
                    "weights" : [
                        W1,
                        ...
                    ]
                },

                "source" : source,
                "target" : target,
            }

        The above format give the flixibility to iterate paths and the
        calculated weights as a :func:`zip` function in forward models.
        """

        augmentedpaths = nx.all_simple_paths(
            self.G, source = self.source, target = self.target
        )

        allpaths = dict(
            paths = dict(
                nodes = [path for path in augmentedpaths]
            ),

            # default class values, decorations
            source = self.source,
            target = self.target,
        )

        # add the edge attribute for weights calculations
        allpaths["paths"]["edges"] = [
            list(pairwise(path)) for path in allpaths["paths"]["nodes"]
        ]

        # calculate the weights based on the given attribute, formula
        allpaths["paths"]["weights"] = [
            [
                self.inspect(
                    edge,
                    component = "edge"
                ).attributes[attribute]
                for edge in path
            ]
            for path in allpaths["paths"]["edges"]
        ]

        allpaths["paths"]["weights"] = [
            sum(weight) if calculate == "additive" else prod(weight)
            for weight in allpaths["paths"]["weights"]
        ]

        allpaths["paths"]["costs"] = [
            sum([
                nxcostfunc(
                self.G,
                source = source,
                target = target,
                weight = attribute
                )
                for source, target in path
            ])
            for path in allpaths["paths"]["edges"]
        ]

        # remove edges, if rtype is nodes::
        if rtype == "nodes":
            _ = allpaths["paths"].pop("edges")
        elif rtype == "edges":
            _ = allpaths["paths"].pop("nodes")
        elif rtype == "complete":
            pass # no deletion, default
        else:
            raise ValueError(f"Return Type `{rtype}` is not Defined")

        return allpaths


    def __set_path__(self, source : GraphNode, target : GraphNode):
        source, target = list(map(
            lambda x : x.label if isinstance(x, GraphNode) else x,
            [source, target]
        ))

        assert source in self.dnodes.keys() if source else True, \
            "Source Node is not a part of the Graph"
        assert source in self.dnodes.keys() if source else True, \
            "Target Node is not a part of the Graph"
        
        assert not source == target == None, \
            "Both Source & Target Node cannot be None"
        
        return source, target
