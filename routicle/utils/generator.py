# -*- encoding: utf-8 -*-

"""
Generator Function(s) to Create Graph Objects
"""

from uuid import uuid4 as UUIDx
from typing import Any, Dict, Generator, Iterable, Optional

def create_nodes(
        n : int,
        ntype : object,
        prefix : str = "N",
        attributes : Optional[Iterable[Dict[str, Any]]] = [],
        **kwargs
    ) -> Generator:
    """
    Create an Iterable of Multiple Nodes with a Prefix

    The function creates an iterable that can generate multiple nodes
    (of choice) and return as a generator or a list.

    :type  n: int
    :param n: Number of nodes to be required for a particular type.
        The index starts at zero.

    :type  ntype: object
    :param ntype: Type of node, this must be a type of node defined
        under the ``components/nodes.py`` or can be a base node class.

    :type  prefix: str
    :param prefix: A prefix string that can be added at the beginning
        of the node name for easy identification.

    :type  attributes: iterable
    :param attributes: List of dynamic attributes based on the type of
        node. The attributes must be the same length as ``n`` and the
        values must be a dict. Check example usage for more details.

    Keyword Argument(s)
    -------------------

    Additional optional controls of the function can be done through
    the use of the following keyword arguments.

        * **namegen** (*callable*): A callable function to generate
          the attribute ``name`` for each of the node. Defaults to the
          string formatter ``f"{prefix}{str(idx).zfill(len(str(n)))}"``
          where ``idx`` is ``range(n)`` and is formatted to be of same
          size by using ``.zfill(...)`` function.

    Example Usage(s)
    ----------------

    The module once imported, the function can be invoked using any of
    the base node type defined in the system.

    ..code-block:: python

        import routicle as ro # module import
        from routicle.components.base import GraphNode

        # example to define n base graph nodes, with defaults
        nodes = list(ro.utils.generator.create_nodes(
            2, ntype = GraphNode
        ))

    The function is a dynamic one, and one can define any set of
    arguments and pass as a dictionary for the underlying node type.
    """

    assert len(attributes) in [n, 0], \
        f"Attribute must be [] or the number must match N (={n})."
    
    # ! Create a blank attribute, if not already defined
    attributes = attributes if attributes else [dict()] * n
    
    # ? Keyword arguments defination with defaults
    namegen = kwargs.get(
        "namegen",
        lambda pre, idx, n : f"{pre}{str(idx).zfill(len(str(n)))}"
    )

    # generator: use `next()` or `list(...)`
    for idx in range(n):
        attribute = attributes[idx] # current attribute

        # ? Name Attribute:: Generate using a Callable Function
        attribute["name"] = namegen(prefix, idx, n)
        yield ntype(**attribute)
