import os

import networkx as nx
import pandas as pd

from graph_coloring.exceptions import InvalidGraphException


def get_vertices_of_degree_n(graph: nx.Graph, n, at_least=False, up_to=False):
    """
    Get all vertices in the given graph of degree n (or from n upwards if indicated)
    :param graph: Graph to get degrees from
    :param n: The degree to be gotten
    :param at_least: Bool indicating if degrees are exactly n or from n upwards
    :param up_to: Bool indicating if degrees are exactly n or up to n
    :return: Vertices that fulfill the given requirements
    """
    if at_least:
        return [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] >= n]
    if up_to:
        return [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] <= n]

    return [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] == n]


def intersection(list1, list2, sort=False):
    """
    Get the intersection of 2 lists.
    :param list1: List 1 to intersect
    :param list2: List 2 to intersect
    :param sort: Sort the intersected list
    :return: All elements in both lists
    """
    intersected = list(set(list1) & set(list2))

    if not sort:
        return intersected

    intersected.sort()

    return intersected


def get_possible_colors(neighbors, color_dict):
    """
    Get the possible remaining colors after removing the ones already in use by the given neighbors.
    :param neighbors: List of neighbors
    :param color_dict: Dict containing the available colors for each node
    :return: A list of possible colors
    """
    possible_colors = ['red', 'green', 'blue']
    neighbor_colors = []

    for neighbor in neighbors:
        try:
            neighbor_colors.append(color_dict[neighbor])
        except KeyError:
            # print(f"Neighbor {neighbor} not yet colored")
            pass

    for neighbor_color in set(neighbor_colors):
        possible_colors.remove(neighbor_color)

    return possible_colors


def color_low_degree_vertices(graph, low_degree_vertices, colors_dict):
    """
    Color the nodes with degree <= 2 greedily, since there is always a color that's still available.
    :param graph: Graph to color nodes in
    :param low_degree_vertices: List of nodes with degree <= 2
    :param colors_dict: Dict containing the available colors for each node
    """
    for low_degree_vertex in low_degree_vertices:
        neighbors = list(nx.neighbors(graph, low_degree_vertex))
        possible_colors = get_possible_colors(neighbors, colors_dict)
        colors_dict[low_degree_vertex] = possible_colors[0]


def convert_path_to_dict(graph_path):
    path_parts = graph_path.split('-')

    if path_parts[6] != 'None':
        graph_type = 'p7_c3'
    elif path_parts[10] == 'True':
        graph_type = 'planar'
    elif path_parts[14] == 'True':
        graph_type = 'locally_connected'
    else:
        raise InvalidGraphException('Expected at least one type to match...')

    return {
        'nodes': path_parts[2],
        'p': path_parts[4],
        'graph_type': graph_type
    }


def write_results(graph_name, method, time):
    path = f"./results/result.csv"

    if not os.path.exists("results/"):
        os.makedirs("results/")

    if not os.path.isfile(path):
        df = pd.DataFrame(columns=["nodes", "p", "graph_name", "method", "execution_time"])
        df.to_csv(path)

    graph_dict = convert_path_to_dict(graph_name)

    data = {
        'nodes': [graph_dict['nodes']],
        'p': [graph_dict['p']],
        'graph_type': [graph_dict['graph_type']],
        'method': [method],
        'execution_time': [time],
    }

    # Make data frame of above data
    df = pd.DataFrame(data)

    # append data frame to CSV file
    df.to_csv(path, mode='a', index=False, header=False)
