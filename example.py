import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

from drawing import chord_diagram


def networkx_drawing_example(graph, img_path):
    fig, ax = plt.subplots(figsize=(10, 10))

    nx.draw_circular(graph, ax=ax)
    ax.set_title("Graph drawn with networkx")

    fig.savefig(img_path)


def simple_example(graph, img_path):
    fig, ax = plt.subplots(figsize=(10, 10))

    ax = chord_diagram(graph, ax)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_title("A simple graph drawn better")

    fig.savefig(img_path)


def cells_network_example(graph, img_path):
    fig, ax = plt.subplots(figsize=(10, 10))
    chord_diagram(graph, ax)
    ax.set_title(img_path)

    fig.savefig("images/2_cells_network.png")


def not_circular_layout_example(img_path):
    from drawing import draw_graph_edges

    graph = nx.Graph()

    # Create a random graph with self-loops
    graph.add_nodes_from(range(10))

    while len(graph.edges) < 30:
        node_i, node_j = np.random.choice(graph.nodes, 2)
        graph.add_edge(node_i, node_j)
        graph.edges[(node_i, node_j)]["weight"] = np.random.randint(1, 5)

    pos = nx.kamada_kawai_layout(graph)

    fig, ax = plt.subplots(figsize=(10, 10))
    nx.draw_networkx_nodes(graph, pos, ax=ax)
    ax = draw_graph_edges(graph, pos, ax)
    ax.set_title("Cells communication network")

    fig.savefig(img_path)


def cells_communication_graph():
    cell_types = ("RPS expressing", "B", "CD4 T", "CD14 Monocytes", "NK",
                  "CD8 T", "FCGR3A Monocytes", "Dendritic", "Megakaryocytes")
    communication_network = np.array(
        [
            (1, 0, 1, 1, 1, 1, 1, 1, 0),
            (1, 0, 1, 2, 1, 1, 2, 2, 0),
            (0, 0, 1, 1, 1, 1, 1, 1, 0),
            (0, 0, 0, 3, 0, 0, 3, 3, 0),
            (1, 0, 1, 3, 1, 1, 3, 3, 0),
            (0, 0, 0, 1, 0, 0, 1, 1, 0),
            (0, 1, 0, 3, 0, 0, 3, 3, 1),
            (0, 0, 0, 3, 0, 0, 3, 3, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 1)
        ]
    )
    df = pd.DataFrame(communication_network, index=cell_types, columns=cell_types)

    return nx.DiGraph(df)


if __name__ == "__main__":
    np.random.seed(42)

    graph = nx.DiGraph(
        np.array([
            [1, 2, 1, 3, 5],
            [1, 0, 3, 0, 0],
            [1, 1, 3, 0, 1],
            [0, 0, 2, 0, 1],
            [1, 1, 1, 1, 1]
        ])
    )

    networkx_drawing_example(graph, img_path="images/0_simple_graph_networkx.png")
    simple_example(graph, img_path="images/1_simple_graph.png")

    cells_communication_graph = cells_communication_graph()

    cells_network_example(cells_communication_graph, img_path="Cells communication network")
    networkx_drawing_example(cells_communication_graph, img_path="images/3_nx_cells_network.png")
    not_circular_layout_example(img_path="images/4_not_circular_layout.png")
