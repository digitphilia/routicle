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

        * **uselabels** (*bool*): A node has an unique identity which
            defaults to ``uuid.uuid4`` and a display label in the
            graph. By default, if a label is not defined then it is
            the same as the unique identity. On setting the value to
            ``True`` the unique identity and the label is generated
            as ``{N001, N002, ...}`` else, the label is same, while
            the unique identity is a ``uuid.uuid4`` string object.
            Defaults to True.

        * **genindex** (*bool*): By default, if an attribute is passed,
            then the function expects all the default attributes to be
            defined. However, we give the privilege to generate the
            unique identity of the attribute by passing partial values.
            Defaults to False.

        * **genlabel** (*bool*): Like ``genindex`` generate the label
            if partial list is passed. Default to False.

        * **ovindex** (*bool*): Overwrite index value with the passed
            label value - this can be useful when a partial attribute
            is passed and ``genindex == False`` is defined. Defaults
            to False.

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
    uselabels = kwargs.get("uselabels", True)

    genindex = kwargs.get("genindex", False)
    genlabel = kwargs.get("genlabel", False)

    ovindex = kwargs.get("ovindex", False)

    # generator: use `next()` or `list(...)`
    for idx in range(n):
        attribute = attributes[idx] # current attribute

        # ? Label Attribute:: Generate or Use Defaults
        _label = f"{prefix}{str(idx).zfill(len(str(n)))}"
        _label = _label if genlabel else attribute.get("label", None)

        # ? Unique Identity Attribute:: Generate or Override
        _cidx = attribute["label"] if uselabels or ovindex else \
            str(UUIDx()) if genindex else attribute.get("cidx", None)

        # ? Overwrite or define the labels from the above vars
        attribute["cidx"] = _cidx
        attribute["label"] = _label

        yield ntype(**attribute)
