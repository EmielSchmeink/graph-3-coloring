import networkx as nx
from matplotlib import pyplot as plt


def draw_graph(graph, node_colors, edge_colors=None):
    if nx.is_planar(graph):
        nx.draw_planar(graph, node_color=node_colors, edge_color=edge_colors, with_labels=True)
    else:
        nx.draw_kamada_kawai(graph, node_color=node_colors, edge_color=edge_colors, with_labels=True)
    plt.show()


def color_edges(graph, edges):
    for e in graph.edges():
        graph[e[0]][e[1]]['color'] = 'black'

    for e in edges:
        graph[e[0]][e[1]]['color'] = 'red'

    return [graph[e[0]][e[1]]['color'] for e in graph.edges()]
