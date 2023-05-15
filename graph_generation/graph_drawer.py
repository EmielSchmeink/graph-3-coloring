import networkx as nx
import numpy as np
from matplotlib import pyplot as plt


def draw_graph_with_color_from_dict(graph, color_dict):
    pos = nx.kamada_kawai_layout(graph)

    nodes = {
        'red': [],
        'blue': [],
        'green': [],
        '#1f78b4': list(graph.nodes())
    }

    for key, value in color_dict.items():
        nodes[value].append(key)
        nodes['#1f78b4'].remove(key)

    for node_color, nodelist in nodes.items():
        nx.draw(graph, pos, nodelist=nodelist, node_color=node_color, labels={node: node for node in graph.nodes()})

    plt.show()


def draw_planar_directed(graph):
    nx.draw_planar(graph.to_directed(), arrows=True, with_labels=True)
    plt.show()


def draw_graph(graph, node_colors, edge_colors=None):
    if nx.is_planar(graph):
        nx.draw_planar(graph, node_color=node_colors, edge_color=edge_colors, with_labels=True)
    elif nx.is_bipartite(graph) and len(list(nx.connected_components(graph))) == 1:
        w = nx.bipartite.sets(graph)[0]
        nx.draw(graph, pos=nx.bipartite_layout(graph, w),
                node_color=node_colors, edge_color=edge_colors, with_labels=True)
    else:
        nx.draw_spring(graph, node_color=node_colors, edge_color=edge_colors, with_labels=True)
    plt.show()


def draw_flow(graph, num_k13, num_leaves):
    pos = nx.spring_layout(graph)
    pos['source'] = np.array([0.5, 1.5])
    pos['target'] = np.array([0.5, 0])

    num_k13_left = num_k13
    num_leaves_left = num_leaves

    for node in graph:
        if 'k13_' in node:
            num_k13_left -= 1
            pos[node] = np.array([num_k13_left/num_k13, 1])
        elif 'source' not in node and 'target' not in node:
            num_leaves_left -= 1
            pos[node] = np.array([num_leaves_left/num_leaves, 0.5])

    nx.draw(
        graph, pos=pos, edge_color='black', width=1, linewidths=1,
        node_size=500, node_color='pink', alpha=0.9,
        labels={node: node for node in graph.nodes()}
    )
    nx.draw_networkx_edge_labels(graph, pos=pos,
                                 edge_labels={(edge[0], edge[1]): edge[-1]
                                              for edge in graph.edges.data('capacity', default=0)})
    plt.show()


def draw_k13_list(graph, k13_list):
    red_edges = []
    green_edges = []

    for k13 in k13_list:
        red_edges.extend(k13.get_k13_edges())
        green_edges.extend(k13.children_edges)

    draw_graph(graph, None, edge_colors=color_edges(graph, red_edges, green_edges))


def color_edges(graph, red_edges, green_edges):
    for e in graph.edges():
        graph[e[0]][e[1]]['color'] = 'black'

    for e in red_edges:
        graph[e[0]][e[1]]['color'] = 'red'

    for e in green_edges:
        graph[e[0]][e[1]]['color'] = 'green'

    return [graph[e[0]][e[1]]['color'] for e in graph.edges()]
