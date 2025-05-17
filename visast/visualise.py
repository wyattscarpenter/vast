"""visualise.py Visualises an Abstract Syntax Tree

VisAST - Building and visualising Abstract Syntax Trees for Python code.

Authors: Jesse Phillips <james@jamesphillipsuk.com>

"""

import ast
from typing import Literal, TypeVar, assert_never
import networkx as nx
import EoN #type: ignore[import-untyped]
import matplotlib.pyplot as plt
from pyvis.network import Network #type: ignore[import-untyped]


def graph(a: ast.Module, plotter: Literal["matplotlib", "pyvis"] = "matplotlib", really_show: bool = True) -> None:
    """ Builds a visualisation of the provided AST.

    Args:
        a (AST): The abstract syntax tree.
    """
    g: nx.DiGraph[str] = nx.DiGraph()
    rootNodeID = "noRoot"
    edges: list[list[str]] = []
    labelDictionary = {}
    # Walk the tree, breadth-first, noting all edges.
    for node in ast.walk(a):
        nodeID = str(node.__class__) + str(id(node))  # Unique name
        # ...Is this actually unique, or is the id reused? hash() would also be a candidate if so.
        nodeLabel = str(node.__class__).split("ast.")[1].split("'>")[0]
        if isinstance(node, ast.Constant):
            nodeLabel += " " + str(node.value)
        elif isinstance(node, ast.FunctionDef):
            nodeLabel += " " + str(node.name)
        labelDictionary[nodeID] = nodeLabel

        if rootNodeID == "noRoot":
            rootNodeID = nodeID

        for child in ast.iter_child_nodes(node):
            childNodeID = str(child.__class__) + str(id(child))
            for edge in edges:
                if edge[1] == childNodeID:
                    childNodeID += str(1)  # IDs aren't unique.  Fix.

            # If child is at the bottom of the tree, it won't get walked.
            # Label it manually.
            if labelDictionary.get(childNodeID) is None:
                childLabel = str(child.__class__
                                 ).split("t.")[1].split("'>")[0]
                if isinstance(child, ast.Constant):
                    childLabel += " " + str(child.value)

                labelDictionary[childNodeID] = childLabel
                if isinstance(node, ast.Load|ast.Store|ast.Del):
                    if hasattr(node, "id"):
                        nodeLabel = str(node.id) #pyright: ignore[reportAttributeAccessIssue] #I believe the problem is, as of 2025-05-14, that the typeshed stubs for ast.expr_context is incomplete. Mypy narrows based on hasattr, so our explicit check avoids that problem, but pyright doesn't, see https://github.com/microsoft/pyright/issues/6717, so we would need to have another way of detecting if id is available, such as with richer type annotations.
                        labelDictionary[nodeID] = nodeLabel

            g.add_edge(nodeID, childNodeID)
            edges.append([nodeID, childNodeID])
    __plotGraph(g, rootNodeID, labelDictionary, plotter, really_show)


def __colourNodes(labels: dict[str, str]) -> list[str]:
    """ Private.  Colours important nodes in an AST.
    For python 3.9 support, this uses an if statement.  It would be better
    in 3.10+ to use a match/case block.

    Args:
        labels(dict(str)): the labels for the AST.  Search these for features.

    Returns:
        list: the list of colours for nodes in the graph.
    """
    colourMap = []
    for label in labels:
        cleanLabel = label.split("ast.")[1].split("'>")[0]
        if cleanLabel == "Module":
            colourMap.append("#b3ffb3")
        elif cleanLabel == "ClassDef":
            colourMap.append("#ffffb3")
        elif cleanLabel == "FunctionDef":
            colourMap.append("#ffb3ff")
        else:
            colourMap.append("#1f78b4")
    return colourMap

T = TypeVar('T') # if we didn't support Python <3.12, we could use type parameter syntax instead. Also, this TypeVar is a bit of an embellishment, because we only ever use this for a DiGraph[str], anyway.
def __plotGraph(graph: "nx.DiGraph[T]", rootNodeID: str, labels: dict[str,str], plotter: Literal["matplotlib", "pyvis"] = "matplotlib", really_show: bool = True) -> None:
    """ Private.  Plots a given networkx DiGraph as an AST.

    Args:
        graph (nx.DiGraph): the graph to plot.
        rootNodeID (string): the root node of the graph represented as a tree.
        labels (dict(string)): the labels for the nodes in the graph.
        really_show (bool): this can be set to False to disable actually displaying the plot, for testing purposes
    """
    # Make the graph look like a tree using hierarchy_pos.
    pos = EoN.hierarchy_pos(graph, rootNodeID)
    colourMap = __colourNodes(labels)
    nx.draw_networkx_nodes(graph, pos=pos, alpha=0.6, node_color=colourMap) #pyright: ignore[reportArgumentType] # This is a result of (maybe: pyright's parameter type inference for unannotated arguments with defaults, and) the fact that https://github.com/python/typeshed/pull/14057 isn't merged yet.
    nx.draw_networkx_edges(graph, pos=pos, alpha=0.5)
    nx.draw_networkx_labels(graph, pos=pos, labels=labels)

    plt.title("Abstract Syntax Tree:")
    plt.tight_layout(pad=0)
    plt.axis("off")
    if really_show:
        if plotter == "matplotlib":
            plt.show()  # Tada!
        elif plotter == "pyvis":
            nt = Network(directed=True, layout=True)#, heading="Abstract Syntax Tree") #if the heading is set, it's doubled. Very odd.
            nt.from_nx(graph)
            #Oddly these properties don't seem to come along for the ride:
            for node in nt.nodes:
                node["color"] = __colourNodes({node["label"] : "dummystr"})[0]
                node["label"] = labels[node["label"]]
            nt.show("tmp_pyvis-based_ast_visualization.html", notebook=False)
        else:
            assert_never(plotter)
