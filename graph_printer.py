import networkx as nx
from matplotlib import pyplot as plt


def draw_graph(graph):
    if nx.is_planar(graph):
        nx.draw_planar(graph, with_labels=True)
    else:
        nx.draw_kamada_kawai(graph, with_labels=True)
    plt.show()
