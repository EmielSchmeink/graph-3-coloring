import itertools

import networkx as nx


def check_safety_k_4_6(multigram, graph):
    """
    Check for the given tetra- or hexagram if they are safe.
    :param multigram: Multigram with 4 or 6 vertices
    :param graph: The graph to find paths in
    :return: Whether the given multigram is safe or not
    """
    # By definition of the paper
    v_1 = multigram[0]
    v_3 = multigram[2]

    paths = list(nx.all_simple_paths(graph, v_1, v_3, 3))

    for path in paths:
        for node in path:
            if node not in multigram:
                return False
    return True


def get_distinct_neighbor(pentagram_node, pentagram, graph):
    """
    Get the distinct neighbor of a pentagram node.
    :param pentagram_node: Node to get the distinct neighbor for
    :param pentagram: Pentagram the node is in
    :param graph: Graph the neighbor is in
    :return: The distinct neighbor of the pentagram node
    """
    node_neighbors = graph.neighbors(pentagram_node)
    for node_neighbor in node_neighbors:
        if node_neighbor not in pentagram:
            return node_neighbor


def get_distinct_neighbors(multigram, graph):
    """
    Get the distinct neighbors of a pentagram or decagram.
    :param multigram: The penta or decagram to find the distinct neighbors for
    :param graph: Graph to find the neighbors in
    :return: List of distinct neighbors for each node of the pentagram
    """
    distinct_neighbors = []

    for node in multigram:
        distinct_neighbors.append(get_distinct_neighbor(node, multigram, graph))

    if len(distinct_neighbors) != 5:
        return False

    return distinct_neighbors


def check_safety_pentagram(multigram, graph):
    """
    Check the pentagram for safety as according to the paper.
    :param multigram: Pentagram to check safety for
    :param graph: Graph to do the safety checks in
    :return Bool whether the pentagram is safe or not
    """
    distinct_neighbors = get_distinct_neighbors(multigram, graph)

    for neighbor_pair in list(itertools.combinations(distinct_neighbors, 2)):
        if graph.has_edge(neighbor_pair[0], neighbor_pair[1]) or graph.has_edge(neighbor_pair[1], neighbor_pair[0]):
            return False

    x_2 = distinct_neighbors[1]
    x_3 = distinct_neighbors[2]
    x_4 = distinct_neighbors[3]
    v_3 = multigram[2]
    v_4 = multigram[3]
    v_5 = multigram[4]
    graph_without_multigram = graph.copy()
    graph_without_multigram.remove_nodes_from(multigram[0:4])

    # No path of length at most 3 between x_2 and v_5, so length <= 3
    paths = list(nx.all_simple_paths(graph_without_multigram, x_2, v_5, 3))

    if len(paths) > 0:
        return False

    paths = list(nx.all_simple_paths(graph_without_multigram, x_3, x_4, 3))

    for path in paths:
        # 3 nodes, so length 2
        if len(path) != 3:
            return False

        completed_path = path.copy()
        completed_path.append(v_4)
        completed_path.insert(0, v_3)

        subgraph = nx.induced_subgraph(graph, completed_path)
        facial_cycles = nx.cycle_basis(subgraph)

        if not len(facial_cycles) == 1:
            return False

        if not len(facial_cycles[0]) == 5:
            return False

    return True


def check_safety_decagram(multigram, graph):
    """
    Check the decagram for safety as according to the paper.
    :param multigram: Decagram to check safety for
    :param graph: Graph to do the safety checks in
    :return Bool whether the decagram is safe or not
    """
    distinct_neighbors = get_distinct_neighbors(multigram, graph)

    x_1 = distinct_neighbors[0]
    x_3 = distinct_neighbors[2]

    if x_1 == x_3:
        return False

    if graph.has_edge(x_1, x_3):
        return False

    # No path of length at most 2 between x_1 and x_3, so length <= 2
    paths = list(nx.all_simple_paths(graph, x_1, x_3, 2))

    if len(paths) > 0:
        return False

    return True


def check_if_k_4_is_octagram(multigram, graph):
    """
    Check if the given multigram with 4 vertices is an octagram.
    :param multigram: Multigram with 4 vertices
    :param graph: Graph to check degrees in
    :return: Whether the given multigram is an octagram or not
    """
    is_octagram = True
    for node in multigram:
        if graph.degree[node] != 3:
            is_octagram = False
    return is_octagram


def check_if_k_5_is_pentagram(multigram, graph):
    """
    Check if the given multigram with 5 vertices is a pentagram.
    :param multigram: Multigram with 5 vertices
    :param graph: Graph to check degrees in
    :return: Whether the given multigram is a pentagram or not
    """
    # Check that is even a pentagram
    for i in range(4):
        if graph.degree[multigram[i]] != 3:
            return False
    return True


def check_if_k_5_is_decagram(multigram, graph):
    """
    Check if the given pentagram is a decagram.
    :param multigram: Pentagram to check whether it is a decagram
    :param graph: Graph to check degrees in
    :return: Whether the given pentagram is a decagram or not
    """
    # Check if the last vertex is also degree 3, if so => decagram
    if graph.degree[multigram[4]] != 3:
        return False

    return True


def check_multigram_safety(multigram, graph):
    """
    Check for the given multigram if they are safe.
    :param multigram: Vertices of facial walk
    :param graph: The graph to check if the multigram is safe in
    :return: Whether the given multigram is safe or not
    """
    match len(multigram):
        case 1:
            return True
        case 4:
            # Octagram is always safe
            if check_if_k_4_is_octagram(multigram, graph):
                return True, 'octagram'
            else:
                return check_safety_k_4_6(multigram, graph), 'tetragram'
        case 5:
            if not check_if_k_5_is_pentagram(multigram, graph):
                return False, 'pentagram'

            if check_if_k_5_is_decagram(multigram, graph):
                return check_safety_decagram(multigram, graph), 'decagram'

            return check_safety_pentagram(multigram, graph), 'pentagram'
        case 6:
            return check_safety_k_4_6(multigram, graph), 'hexagram'
        case _:
            print('Planar Triangle-free: Facial walk not the correct size...')
            return False, 'nogram'
