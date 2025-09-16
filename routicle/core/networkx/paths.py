# -*- encoding: utf-8 -*-

"""
A Set of Computations based on Paths of a NetworkX Graph
"""

from math import prod
from itertools import pairwise
from typing import Dict, Tuple, Iterable, Callable

import networkx as nx

from routicle.core.networkx.base import nxGraph
from routicle.components.base import PointOfInterest, POIConnector

class PathAnalysis(nxGraph):
    """
    Analyse a Complete Graph Path from Source to Target

    Analyse source and target nodes and trace paths, weights, etc.
    which are availble as an attribute. The internal functions are
    heavily dependent on the :mod:`networkx` module and typically
    returns an interable of paths for further analysis.

    :ivar source, target: Source and target node name or the node
        object of :mod:`routicle.components.base.PointOfInterest`
        instance. Both the values cannot be None, and analysis is done
        on the available nodes.

    Note: Simple wrapper of :mod:`networkx` module are not available,
    and it is recommended to directly use those functions unless the
    functions are required multiple times in forward logics.

    .. code-block:: python

        import networkx as nx
        import routicle.core.networkx as rnx

        # create a model for path analysis from graph
        # source and target can be name or PointOfInterest instances
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
        dnodes : Dict[str, PointOfInterest],
        dedges : Dict[Tuple[str, str], POIConnector],
        initgraph : bool = True,
        source : PointOfInterest | str = None,
        target : PointOfInterest | str = None
    ) -> None:
        super().__init__(
            G = G,
            dnodes = dnodes,
            dedges = dedges,
            initgraph = initgraph
        )
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


    def sortedpaths(
            self,
            sense : int = 1,
            cattribute : str = "costs",
            **kwargs
        ) -> dict:
        """
        Find & Report the K-th Path based on an Objective Function

        The function finds a path based on an objective function which
        is either a "minimization" :attr:`sense = 1` (default) or an
        "maximization" :attr:`sense = -1` problem.

        :type  sense: int
        :param sense: Objective function, which is either a
            minimization problem (``1``, default) or maximization
            problem (:attr:`sense == -1`).

        :type  cattribute: str
        :param cattribute: Cost attribute to consider for calculation
            and ordering of paths. The typical cost attributes are
            "weights" and "costs" which have a different meaning.
            
        Keyword Arguments
        -----------------

        List of keyword arguments which are typical for the internal
        :func:`getpaths` function.

            * **attribute** (*str*) - Path attributes for calculation
                of augmented path cost.

            * **calculate** (*str*) - Calculation of attribute in the
                desired format, i.e., sum or product mode.

            * **nxcostfunc** (*callable*) - Cost function that is
                using the internal :mod:`networkx` module.

        For more information on the above keyword argument, check the
        internal function documentation. All the values defaults to
        the model function.

        Example Usage(s)
        ----------------

        The function returns a sorted dictionary of paths which has
        all the items from the :func:`getpaths()` to the sense defined
        in the function.

        .. code-block:: python

            import routicle.core.networkx as rnx
            ...

            # define path analysis model from source to target
            model = rnx.PathAnalysis(
                G, dnodes = dnodes, dedges = dedges,
                source = dnodes["V1"], target = dnodes["P4"]
            )

            # you can get the unordered all the paths, with costs like:
            print(model.getpaths())

            # or, get an ordered list which is a derived function:
            print(model.sortedpaths())
            >> ...

            # pulp nomenclature, for maximizing the weights
            print(model.sortedpaths(
                cattribute = "weights", sense = -1
            ))
            >> ...

        The function is customized as per business requirement, and
        is always :mod:`pandas` compatible.
        """

        paths = self.getpaths(
            attribute = kwargs.get("attribute", "weight"),
            calculate = kwargs.get("calculate", "multiplicative"),
            nxcostfunc = kwargs.get(
                "nxcostfunc", nx.dijkstra_path_length
            )
        )["paths"]

        n = len(paths[cattribute]) # raise key error, intentional
        assert sense in [1, -1], "Unknow Value for Sense."

        def sortkey(i : int) -> tuple:
            """
            A Sub-Function to Get an Ordered List

            Get an ordered lists of length ``n`` as the length of the
            attributes from paths in sorted order or user choice.
            """

            return (
                paths[cattribute][i] is None, paths[cattribute][i]
            )

        ordered = sorted(
            range(n), key = sortkey,
            reverse = False if sense == 1 else True
        )

        spaths = dict(paths = {
            k : [ vi for _, vi in sorted(zip(ordered, v)) ]
            for k, v in paths.items()
        })

        # keep the dictionary structure as same as self.getpaths()
        spaths |= dict(source = self.source, target = self.target)

        return spaths


    def __set_path__(
            self,
            source : PointOfInterest,
            target : PointOfInterest
        ):
        source, target = list(map(
            lambda x : x.name if isinstance(x, PointOfInterest) else x,
            [source, target]
        ))

        assert source in self.dnodes.keys() if source else True, \
            "Source Node is not a part of the Graph"
        assert source in self.dnodes.keys() if source else True, \
            "Target Node is not a part of the Graph"
        
        assert not source == target == None, \
            "Both Source & Target Node cannot be None"
        
        return source, target
