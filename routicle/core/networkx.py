# -*- encoding: utf-8 -*-

"""
An Abstract Base Method for Routicle Optimization
"""

from abc import ABC
from math import prod
from itertools import pairwise
from typing import Dict, Tuple, Callable, Iterable

import networkx as nx

from routicle.components.base import PointOfInterest, POIConnector

class nxGraph(ABC):
    """
    NetworkX Graph Base Object for Routicle Module

    An abstract base class is defined of :mod:`networkx` components
    like Graph, nodes and edges definations for route optimization and
    inventory management functions. The base function models all the
    components into a standard format for analysis.

    :ivar G: A :mod:`networkx.Graph` object which is valid and can be
        any of the supported types - directed, multi-graph, etc.

    :ivar dnodes: A dictionary of nodes of the graphs, where the key
        is the "name" of the node and the node is any of the type of
        defined under :mod:`routicle.components.nodes` module. All the
        additional attributes must be associated with the nodes for
        any relevant calculations.

    :ivar dedges: A dictionary of edges of the graph in the format of
        (``u``, ``v``) as the dictionary key and edge is any of the
        derived edge object from :mod:`routicle.components` module.

    :ivar initgraph: Initialize graph with the provided nodes and the
        edges informations. If set to True (default), then internally
        all the edges and nodes are created.

    Basic Usage(s)
    --------------

    The ``nxGraph`` is a type of :mod:`networkx.Graph` component which
    is the core component based on which any type of calculations and
    forward integration with external modules like :mod:`pulp` or
    :mod:`ortools` is also done.

    .. code-block:: python

        import networkx as nx # actual module
        import routicle.core.networkx as rnx

        # define sets of nodes, edges using routicle.components
        nodes = ...
        edges = ...

        # convert the nodes, edges to dnodes and dedges as dictionary
        dnodes = { node.name : node for node in nodes }
        dedges = { (u.name, v.name) : edge for ... }

        # model graph is always a routicle component
        network = rnx.nxGraph(
            G = nx.DiGraph() # created a directed graph
            dnodes = dnodes, dedges = dedges
        )

    The ``routicle.nxGraph`` is also designed to calculate and find
    the shortest path using various algorithms like Dijkstra/A* as per
    the end user requirement.

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
        initgraph : bool = True
    ) -> None:
        self.G = G

        # initialize graph with nodes and edges, on true
        if initgraph:
            self.__init_graph__(dnodes = dnodes, dedges = dedges)

        # ? The graph components from routicle
        self.dnodes = self.__set_dnodes__(G = self.G, nodes = dnodes)
        self.dedges = self.__set_dedges__(G = self.G, edges = dedges)


    def inspect(
        self,
        name : str | Tuple[str, str],
        component : str = "node"
    ) -> PointOfInterest | POIConnector:
        """
        Inspect the Graph and Return a Valid Object (if exists)

        The graph can now be inspected by passing either a node name
        or an edge tuple in the defined :attr:`dnode` or :attr:`dedge`
        format and the function returns the underlying graph component
        which is always a subclass of :attr:`routicle.components.base`
        objects, else raises assertion error.

        .. code-block:: python

            import routicle.core.networkx as rnx

            # generate a networkx graph and define nodes, edges
            # and, create an rnx.nxGraph object with above details
            graph = rnx.nxGraph(
                G = G, dnodes = dnodes, dedges = dedges
            )

            # inspect a node from the graph::
            print(graph.inspect("P0"))
            >> cidx='a54834fb' name='P0' image=...

            # inspect an edge from the graph::
            print(graph.inspect(("V2", "L0"), component = "edge"))
            >> cidx='898a8bca' unode=... vnode=...

        The utility function is useful for quick inspection and lookup
        of calculated attributes from an underlying derived edge like
        :attr:`routicle.components.edges.TimeCostEdge` objects.
        """

        return self.__get_component__(component = component)[name]


    def getbycidx(
            self,
            cidx : str,
            component : str = "node"
        ) -> PointOfInterest | POIConnector:
        """
        Get the Node/Edge Element from the CIDX Attribute

        Each component of the network (namely ``nodes`` and ``edges``)
        should be initialized with an unique identity to maintain
        consistency and easy lookup by a developer during the debug
        process. The function returns a component based on the key.

        :type  cidx: str
        :param cidx: The unique identity of the component as defined
            under the :attr:`cidx` attribute during initialization.

        :type  component: str
        :param component: Look for either the ``node`` or the ``edge``
            from the network. Use the network callables to find the
            node/edge details.
        """

        component = self.__get_component__(component = component)
        return [c for c in component.values() if c.cidx == cidx][0]


    def alter(self, reverse : bool, undirected : bool) -> nx.Graph:
        """
        Format the Graph by using In-Built Functionalities

        Format the graph using in-built functionalities like reverse
        the order of the graph (if ``nx.DiGraph``) or make the graph
        uniderected, etc. as per requirement. The function returns the
        modified graph, without changing the original format.

        :type  reverse: bool
        :param reverse: Reverse the edges direction, only applicable
            if this is a directed graph and not :attr:`undirected`.

        :type  undirected: bool
        :param undirected: Convert a directed graph to an undirected
            one (if required), defaults to False.
        """

        assert not all([reverse, undirected]), \
            "Invalid Combination (both True), Try Again."

        G = self.G.reverse() if reverse else self.G
        G = G.to_undirected() if undirected else G

        return G


    def adjacent_nodes(
            self,
            node : str,
            reverse : bool = False,
            undirected : bool = False
        ) -> tuple:
        """
        Return a Tuple of Adjacent Nodes for the Selected Node

        Uses the internal graph method to find and return a tuple of
        adjacent nodes from the defined networkx graph.

        :type  node: str
        :param node: The node from the graph, which must be present
            else underlying error is raised.

        :type  reverse: str
        :param reverse: Reverse the edges direction, only applicable
            if this is a directed graph and not :attr:`undirected`.

        :type  undirected: bool
        :param undirected: Convert a directed graph to an undirected
            one (if required), defaults to False.
        """

        G = self.alter(reverse = reverse, undirected = undirected)
        return tuple(G.neighbors(node))
    

    def getpaths(
            self,
            source : PointOfInterest | str,
            target : PointOfInterest | str,
            rtype : str = "complete",
            attribute : str = "weight",
            calculate : str = "multiplicative",
            nxcostfunc : Callable = nx.dijkstra_path_length,
            **kwargs
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

        Keyword Argument(s)
        -------------------

        Additional keyword arguments to manipulate the output and
        presentation are as follows:

            * **roundvalue** (*int*): Round numeric values to desired
              number of numeric place, defaults to None, i.e., no
              rounding.
        """

        roundvalue = kwargs.get("roundvalue", None)

        source, target = self.__set_path__(
            source = source, target = target
        )
        augmentedpaths = nx.all_simple_paths(
            self.G, source = source, target = target
        )

        allpaths = dict(
            paths = dict(
                nodes = [path for path in augmentedpaths]
            ),

            # default class values, decorations
            source = source,
            target = target,
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

        if roundvalue:
            allpaths["paths"]["weights"] = [
                round(value, roundvalue)
                for value in allpaths["paths"]["weights"]
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

        if roundvalue:
            allpaths["paths"]["costs"] = [
                round(value, roundvalue)
                for value in allpaths["paths"]["costs"]
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
            source : PointOfInterest | str,
            target : PointOfInterest | str,
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
            source = source, target = target,
            attribute = kwargs.get("attribute", "weight"),
            calculate = kwargs.get("calculate", "multiplicative"),
            nxcostfunc = kwargs.get(
                "nxcostfunc", nx.dijkstra_path_length
            ),
            **{
                k : v for k, v in kwargs.items()
                if k in ["roundvalue"] # getpaths keyword args
            }
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
        spaths |= dict(source = source, target = target)

        return spaths

    

    def __get_component__(
            self, component : str
        ) -> PointOfInterest | POIConnector:
        """
        Return the Graph Component(s) (Node/Edge) based on Requirement
        """

        component = component.lower()
        assert component in ["node", "edge"], \
            f"Component: {component} is not Valid."

        component = self.dnodes if component == "node" \
            else self.dedges
        
        return component


    def __set_dnodes__(
        self,
        G : nx.Graph,
        nodes : Dict[str, PointOfInterest]
    ) -> Dict[str, PointOfInterest]:
        assert all([ node in nodes.keys() for node in G.nodes ]), \
            "Configuration Error:: Missing D-Nodes."
        
        assert all([ node in G.nodes for node in nodes.keys() ]), \
            "Configuration Error:: Missing Graph Nodes."

        return nodes # return the passed dnodes, after assertion


    def __set_dedges__(
        self,
        G : nx.Graph,
        edges : Dict[Tuple[str, str], POIConnector]
    ) -> Dict[Tuple[str, str], POIConnector]:
        assert all([ edge in edges.keys() for edge in G.edges ]), \
            "Configuration Error:: Missing D-Edges."
        
        assert all([ edge in G.edges for edge in edges.keys() ]), \
            "Configuration Error:: Missing Graph Edges."

        return edges # return the passed dedges, after assertion


    def __init_graph__(
        self,
        dnodes : Dict[str, PointOfInterest],
        dedges : Dict[Tuple[str, str], POIConnector]
    ) -> None:
        nodes, edges = dnodes.values(), dedges.values()

        for node in nodes:
            self.G.add_node(
                node.name, color = node.color, **node.attributes
            )

        for edge in edges:
            self.G.add_edge(
                edge.unode.name, edge.vnode.name, **edge.attributes
            )

        return None
    

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
