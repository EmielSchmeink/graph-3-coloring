import networkx as nx


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
