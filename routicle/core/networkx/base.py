# -*- encoding: utf-8 -*-

"""
An Abstract Base Method for Routicle Optimization
"""

from abc import ABC
from typing import Dict, Tuple

import networkx as nx

from routicle.components.base import GraphNode, GraphEdge

class nxGraph(ABC):
    def __init__(
        self,
        G : nx.Graph,
        dnodes : Dict[str, GraphNode],
        dedges : Dict[Tuple[str, str], GraphEdge]
    ) -> None:
        self.G = G

        # ? The graph components from routicle
        self.dnodes = self.__set_dnodes__(G = self.G, nodes = dnodes)
        self.dedges = self.__set_dedges__(G = self.G, nodes = dedges)


    def inspect(
        self,
        label : str | Tuple[str, str],
        component : str = "node"
    ) -> GraphNode | GraphEdge:
        component = component.lower()
        assert component in ["node", "edge"], \
            f"Component: {component} is not Valid."

        di = self.dnodes if component == "node" else self.dedges
        return di[label] # value assertion on initialization


    def __set_dnodes__(
        self,
        G : nx.Graph,
        nodes : Dict[str, GraphNode]
    ) -> Dict[str, GraphNode]:
        assert all([ node in nodes.keys() for node in G.nodes ]), \
            "Configuration Error:: Missing D-Nodes."
        
        assert all([ node in G.nodes for node in nodes.keys() ]), \
            "Configuration Error:: Missing Graph Nodes."

        return nodes # return the passed dnodes, after assertion


    def __set_dedges__(
        self,
        G : nx.Graph,
        edges : Dict[Tuple[str, str], GraphEdge]
    ) -> Dict[Tuple[str, str], GraphEdge]:
        assert all([ edge in edges.keys() for edge in G.edges ]), \
            "Configuration Error:: Missing D-Edges."
        
        assert all([ edge in G.edges for edge in edges.keys() ]), \
            "Configuration Error:: Missing Graph Edges."

        return edges # return the passed dedges, after assertion
