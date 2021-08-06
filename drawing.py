from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath  # To prevent collision with pathlib.Path
import matplotlib.patches as patches
import networkx as nx
import numpy as np


def normalize_vector(vector: np.array, normalize_to: float) -> np.array:
    """Make `vector` norm equal to `normalize_to`

    vector: np.array
        Vector with 2 coordinates
    normalize_to: float
        A norm of the new vector

    Returns
    -------
    Vector with the same direction, but length normalized to `normalize_to`
    """

    vector_norm = np.linalg.norm(vector)

    return vector * normalize_to / vector_norm


def orthogonal_vector(point: np.array, width: float,
                      normalize_to: Optional[float] = None) -> np.array:
    """Get orthogonal vector to a `point`

    point: np.array
        Vector with x and y coordinates of a point
    width: float
        Distance of the x-coordinate of the new vector from the `point` (in orthogonal direction)
    normalize_to: Optional[float] = None
        If a number is provided, normalize a new vector length to this number

    Returns
    -------
    Array with x and y coordinates of the vector, which is orthogonal to the vector
    from (0, 0) to the `point`
    """
    EPSILON = 0.000001

    x = width
    y = -x * point[0] / (point[1] + EPSILON)

    ort_vector = np.array([x, y])

    if normalize_to is not None:
        ort_vector = normalize_vector(ort_vector, normalize_to)

    return ort_vector


def draw_self_loop(
        point: np.array,
        ax: Optional[plt.Axes] = None,
        padding: float = 1.5,
        width: float = 0.3,
        plot_size: int = 10,
        linewidth=0.2,
        color: str = "pink"
) -> plt.Axes:
    """Draw a loop from `point` to itself

    !Important! By "center" we assume a (0, 0) point. If your data is centered around a different
    point, it is strongly recommended to center it around zero. Otherwise, you will probably
    get ugly plots

    Parameters
    ----------
    point: np.array
        1D array with 2 coordinates of the point. Loop will be drawn from and to these coordinates.
    padding: float = 1.5
        Controls how the distance of the loop from the center. If `padding` > 1, the loop will be
        from the outside of the `point`. If `padding` < 1, the loop will be closer to the center
    width: float = 0.3
        Controls the width of the loop
    linewidth: float = 0.2
        Width of the line of the loop
    ax: Optional[matplotlib.pyplot.Axes]:
        Axis on which to draw a plot. If None, a new Axis is generated
    plot_size: int = 7
        Size of the plot sides in inches. Ignored if `ax` is provided
    color: str = "pink"
        Color of the arrow

    Returns
    -------
    Matplotlib axes with the self-loop drawn
    """

    if ax is None:
        fig, ax = plt.subplots(figsize=(plot_size, plot_size))

    point_with_padding = padding * point

    ort_vector = orthogonal_vector(point, width, normalize_to=width)

    first_anchor = ort_vector + point_with_padding
    second_anchor = -ort_vector + point_with_padding

    verts = [point, first_anchor, second_anchor, point]
    codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4]

    path = MplPath(verts, codes)
    patch = patches.FancyArrowPatch(
        path=path,
        lw=linewidth,
        arrowstyle="-|>",
        color=color,
        alpha=0.5,
        mutation_scale=30  # arrowsize in draw_networkx_edges()
    )
    ax.add_patch(patch)

    return ax


def graph_edges_weights(graph: nx.Graph, weight_key: str = "weight") -> dict[tuple, float]:
    """Create a dictionary with the weights of the graph edges

    Parameters
    ----------
    graph: nx.Graph
        Graph, which edges' weights you want to extract
    weight_key: str = "weight"
        What property of the edges to use as a weight. Other functions assume that this is a number

    Returns
    -------
    Dictionary, where keys are edges and values are their weights
    """
    return {edge: graph.edges[edge][weight_key] for edge in graph.edges}


def draw_graph_edge(graph, pos, edge, edge_weight, ax, color, arc_radius=0.2):
    """Draw the given edge of the network"""

    nx.draw_networkx_edges(
        graph,
        pos=pos,
        width=edge_weight,
        edgelist=[edge],
        alpha=0.5,
        edge_color=color,
        ax=ax,
        arrowsize=30,
        connectionstyle=f"arc3,rad={arc_radius}",
        node_size=1000
    )

    return ax


def draw_graph_edges(graph: nx.graph, pos: dict, ax: plt.Axes) -> plt.Axes:
    """Draw graph edges so that edges in the opposite directions look differently

    graph: nx.Graph
        Graph, edges of which you want to draw
    pos: dict
        Dictionary, where keys are nodes and values are their positions. Can be obtained
        through networkx layout algorithms (e. g. nx.circular_layout())
    ax: plt.Axes
        Axis on which draw the edges

    Returns
    -------
    Axis with the edges drawn
    """

    edge_weights = graph_edges_weights(graph)
    edges_to_draw = set(graph.edges)

    for edge in graph.edges:
        if edge not in edges_to_draw:
            continue

        if edge[0] == edge[1]:  # By default, networkx doesn't draw self loops correctly
            draw_self_loop(point=pos[edge[0]], ax=ax, linewidth=edge_weights[edge])
            edges_to_draw.remove(edge)
            continue

        draw_graph_edge(graph, pos, edge, edge_weight=edge_weights[edge], ax=ax, color="pink")
        edges_to_draw.remove(edge)

        # Edges between the same vertices look confusing, if they have the same style
        # So we draw such edges with different colors and curvature
        reverse_edge = (edge[1], edge[0])

        if reverse_edge in graph.edges and reverse_edge in edges_to_draw:
            draw_graph_edge(
                graph,
                pos,
                reverse_edge,
                edge_weight=edge_weights[edge],
                ax=ax,
                color="lightblue",
                arc_radius=0.1
            )
            edges_to_draw.remove(reverse_edge)

    return ax


def chord_diagram(graph: nx.Graph, ax: Optional[plt.Axes] = None) -> plt.Axes:
    pos = nx.circular_layout(graph, center=(0, 0))

    nx.draw_networkx_nodes(graph, pos, ax=ax)
    draw_graph_edges(graph, pos, ax)
    nx.draw_networkx_labels(graph, pos=pos, font_weight="bold", ax=ax)

    return ax
