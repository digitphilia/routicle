# -*- encoding: utf-8 -*-

"""
An Abstract Base Method for Routicle Optimization
"""

from abc import ABC
from typing import Dict, Tuple

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
    """

    def __init__(
        self,
        G : nx.Graph,
        dnodes : Dict[str, PointOfInterest],
        dedges : Dict[Tuple[str, str], POIConnector]
    ) -> None:
        self.G = G

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

        component = component.lower()
        assert component in ["node", "edge"], \
            f"Component: {component} is not Valid."

        di = self.dnodes if component == "node" else self.dedges
        return di[name] # value assertion on initialization


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
