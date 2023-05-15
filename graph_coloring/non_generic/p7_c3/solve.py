import networkx as nx

from graph_coloring.generic.csp.list_sat import list_sat_satisfier
from graph_coloring.misc import intersection
from graph_generation.graph_checker import GraphChecker


def find_induced_cycle(graph, c, checker):
    """
    Find and return an induced cycle of given size in the given graph.
    :param graph: Graph to find an induced cycle in
    :param c: Size of the induced cycle
    :param checker: Checker instance to find an induced cycle
    :return: An induced cycle if it exists
    """
    for edge in graph.edges:
        cycle = checker.check_induced_cycle_using_path(graph, edge, c)
        if len(cycle) != 0:
            return cycle

    return None


def get_T_from_graph(graph, c5):
    """
    Compute the sets T as defined in the paper from the cycle.
    :param graph: Graph to compute the T sets from
    :param c5: Induced 5 cycle
    :return: The sets T_i of nodes with neighbors in c5, c_{i-1} and c_{i+1}
    """
    graph_without_c5 = graph.copy()
    graph_without_c5.remove_nodes_from(c5)
    T = [[], [], [], [], []]

    for i in range(5):
        for node in graph_without_c5.nodes():
            neighbors = list(graph.neighbors(node))
            cycle_vertices = [c5[(i-1) % 5], c5[(i+1) % 5]]
            neighbors_in_cycle = intersection(neighbors, cycle_vertices)
            # Sort them to make sure that there are no issues with indices
            cycle_vertices.sort()
            neighbors_in_cycle.sort()

            if neighbors_in_cycle == cycle_vertices:
                T[i].append(node)

    return T


def get_D_from_graph(graph, c5):
    """
    Compute the sets D as defined in the paper from the cycle.
    :param graph: Graph to compute the D sets from
    :param c5: Induced 5 cycle
    :return: The sets D_i of nodes with neighbor in c5, c_{i}
    """
    graph_without_c5 = graph.copy()
    graph_without_c5.remove_nodes_from(c5)
    D = [[], [], [], [], []]

    for i in range(5):
        for node in graph_without_c5.nodes():
            neighbors = list(graph.neighbors(node))
            cycle_vertices = [c5[i]]
            neighbors_in_cycle = intersection(neighbors, c5)

            if neighbors_in_cycle == cycle_vertices:
                D[i].append(node)

    return D


def remove_color_from_neighbors(graph, node, color_dict, color):
    """
    Remove a given color from the list coloring options from the neighbors of the given node.
    :param graph: Graph to remove the colors from the neighbors from
    :param node: Node to get the neighbors from
    :param color_dict: Dict containing the list coloring options of nodes
    :param color: The color to be removed
    """
    for neighbor in graph.neighbors(node):
        if color in color_dict[neighbor]:
            color_dict[neighbor].remove(color)


def init_color_dict(graph, c5, T, D):
    """
    Initialize the list coloring by removing or assigning the correct colors to the node's list coloring options,
    as defined in the paper.
    :param graph: Graph with nodes that get an initial list coloring
    :param c5: The induced 5 cycle
    :param T: The sets T_i of nodes with neighbors in c5, c_{i-1} and c_{i+1}
    :param D: The sets D_i of nodes with neighbor in c5, c_{i}
    :return: Dict containing the list coloring options of nodes
    """
    graph_without_c5 = graph.copy()
    graph_without_c5.remove_nodes_from(c5)
    color_dict = {node: ['red', 'green', 'blue'] for node in graph.nodes()}
    color_dict[c5[0]] = ['red']
    color_dict[c5[1]] = ['green']
    color_dict[c5[2]] = ['red']
    color_dict[c5[3]] = ['green']
    color_dict[c5[4]] = ['blue']

    for t_1 in T[0]:
        color_dict[t_1] = ['red']
        remove_color_from_neighbors(graph_without_c5, t_1, color_dict, 'red')

    for t_2 in T[1]:
        color_dict[t_2] = ['green', 'blue']

    for t_3 in T[2]:
        color_dict[t_3] = ['red', 'blue']

    for t_4 in T[3]:
        color_dict[t_4] = ['green']
        remove_color_from_neighbors(graph_without_c5, t_4, color_dict, 'green')

    for t_5 in T[4]:
        color_dict[t_5] = ['blue']
        remove_color_from_neighbors(graph_without_c5, t_5, color_dict, 'blue')

    for i, d_i in enumerate(D):
        for node in d_i:
            if color_dict[c5[i]][0] in color_dict[node]:
                color_dict[node].remove(color_dict[c5[i]][0])

    return color_dict


def get_neighbors_of_subset(graph, subset):
    """
    Get the union of neighbors of a subset of nodes from the given graph.
    :param graph: Graph to get neighbors in
    :param subset: The subset of nodes to get neighbors from
    :return: List of unique neighbors of all nodes in subset
    """
    neighbors = []

    for node in subset:
        neighbors.extend(list(graph.neighbors(node)))

    return list(set(neighbors))


def get_neighbors_in_t_of_ccs(graph, ccs, t):
    """
    Get the neighbors of the given connected components that are in the given T_i.
    :param graph: Graph to get neighbors in
    :param ccs: List of connected components
    :param t: The T_i set given
    :return: List of tuples with the connected component, and the neighbors of that connected component in the given T_i
    """
    cc_with_t_neighbors = []

    for cc in ccs:
        neighbors_of_cc = get_neighbors_of_subset(graph, list(cc))
        neighbors_in_t = intersection(neighbors_of_cc, t)
        cc_with_t_neighbors.append((cc, neighbors_in_t))

    return cc_with_t_neighbors


def split_w_and_rest(ccs):
    """
    Split all connected components into W (containing all isolated nodes), and all non-trivial connected components.
    :param ccs: List of connected components
    :return: List of isolated nodes, and list of non-trivial connected components
    """
    w = []
    rest = []

    for cc in ccs:
        if len(cc) == 1:
            w.extend(list(cc))
        else:
            rest.append(list(cc))

    return w, rest


def handle_trivial_w(graph, w, S, color_dict):
    """
    Assign or remove colors to the given isolated node.
    :param graph: Graph to check for neighbors of w
    :param w: An isolated node
    :param S: List of nodes of c5, T, and D
    :param color_dict: Dict containing the list coloring options of nodes
    """
    w_neighbors = list(graph.neighbors(w))
    w_s_intersection = intersection(w_neighbors, S)

    # If all neighbors are missing a color, w can take that color
    for color in ['red', 'green', 'blue']:
        if all(color not in color_dict[w_s] for w_s in w_s_intersection):
            color_dict[w] = [color]
            return

    # If a neighbor has a fixed color, remove that color from the allowed for w
    for w_s in w_s_intersection:
        if len(color_dict[w_s]) == 1:
            fixed_color = color_dict[w_s][0]
            color_dict[w].remove(fixed_color)
            break

    assert False


def handle_ccs(graph, W, T, D, S, ccs_without_s_without_w, color_dict):
    """
    Handle the coloring of the connected components.
    :param graph: Graph to color in
    :param W: List of isolated nodes
    :param T: The sets T_i of nodes with neighbors in c5, c_{i-1} and c_{i+1}
    :param D: The sets D_i of nodes with neighbor in c5, c_{i}
    :param S: List of nodes of c5, T, and D
    :param ccs_without_s_without_w: Leftover connected components after removing S and W
    :param color_dict: Dict containing the list coloring options of nodes
    """
    for i in [1, 2]:
        handle_w_di(graph, W, T, D, S, i, color_dict)
        handle_G_without_S(graph, ccs_without_s_without_w, T, i, color_dict)


def handle_w_di(graph, W, T, D, S, i, color_dict):
    """
    TODO implement fully
    :param graph: Graph to color in
    :param W: List of isolated nodes
    :param T: The sets T_i of nodes with neighbors in c5, c_{i-1} and c_{i+1}
    :param D: The sets D_i of nodes with neighbor in c5, c_{i}
    :param S: List of nodes of c5, T, and D
    :param i: Which D_i and T_i to use
    :param color_dict: Dict containing the list coloring options of nodes
    """
    w_di = W + D[i]
    graph_w_di = nx.induced_subgraph(graph, w_di)

    ccs_graph_w_di = list(nx.connected_components(graph_w_di))
    ccs_with_num_t_neighbors_w_di = get_neighbors_in_t_of_ccs(graph, ccs_graph_w_di, T[i])

    for cc in ccs_with_num_t_neighbors_w_di:
        # Isolated vertex, and thus a trivial cc
        if len(cc[0]) == 1:
            isolated_vertex = list(cc[0])[0]

            if isolated_vertex in W:
                W.remove(isolated_vertex)

            handle_trivial_w(graph, isolated_vertex, S, color_dict)
        else:
            assert False


def handle_G_without_S(graph, ccs_without_s_without_w, T, i, color_dict):
    """
    TODO implement fully
    :param graph: Graph to color in
    :param ccs_without_s_without_w: Leftover connected components after removing S and W
    :param T: The sets T_i of nodes with neighbors in c5, c_{i-1} and c_{i+1}
    :param i: Which T_i to use
    :param color_dict: Dict containing the list coloring options of nodes
    """
    ccs_with_num_t_neighbors_s = get_neighbors_in_t_of_ccs(graph, ccs_without_s_without_w, T[i])

    ccs_with_neighbors = [cc for cc in ccs_with_num_t_neighbors_s if len(cc[1]) > 0]
    if len(ccs_with_neighbors) > 0:
        assert False


def color_remaining_nodes(graph, color_dict):
    """
    Color all remaining nodes in 2-SAT.
    :param graph: Graph to color in
    :param color_dict: Dict containing the list coloring options of nodes
    :return: Dict of the assigned colors for all nodes
    """
    # Don't color the keys with only 1 color again in the list sat, so remove those before checking sat
    nodes_with_options = []
    color_dict_without_options = {}

    for key, value in color_dict.items():
        if len(value) > 1:
            nodes_with_options.append(key)
        else:
            color_dict_without_options[key] = value[0]

    graph_with_options = nx.induced_subgraph(graph, nodes_with_options)
    color_dict_options = {key: color_dict[key] for key in nodes_with_options}

    colors = list_sat_satisfier(graph_with_options, color_dict_options)
    return colors | color_dict_without_options


def color_bipartite(graph):
    """
    Quickly and greedily color a bipartite graph.
    :param graph: Graph to color in
    :return: Dict of the assigned colors for all nodes
    """
    u, v = nx.bipartite.sets(graph)

    colors_dict = {}

    for node in u:
        colors_dict[node] = 'red'

    for node in v:
        colors_dict[node] = 'green'

    return colors_dict


def p7_c3_solve(graph: nx.Graph):
    """
    Get a 3-coloring for the given (P7, C3)-free graph, using the algorithm
    presented in the paper by Flavia Bonomo-Braberman, Maria Chudnovsky, Jan Goedgebeur, Peter Maceli,
    Oliver Schaudt, Maya Stein, and Mingxian Zhong. Better 3-coloring algorithms:
    Excluding a triangle and a seven vertex path. Theoretical Computer Science, 850:98–115, 1 2021. ISSN 0304-3975.
    doi: 10.1016/J.TCS.2020.10.032.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes
    """
    assert len(list(nx.connected_components(graph))) == 1

    if nx.is_bipartite(graph):
        return color_bipartite(graph)

    checker = GraphChecker()
    c5 = find_induced_cycle(graph, 5, checker)

    if c5 is None:
        # TODO handle this case where we must have a C7
        assert False

    T = get_T_from_graph(graph, c5)
    D = get_D_from_graph(graph, c5)
    S = []
    S.extend(c5)
    for t_i in T:
        S.extend(t_i)
    for d_i in D:
        S.extend(d_i)

    # Make sure we only get the unique vertices
    S = list(set(S))

    color_dict = init_color_dict(graph, c5, T, D)

    graph_without_s = graph.copy()
    graph_without_s.remove_nodes_from(S)
    ccs_graph_without_s = list(nx.connected_components(graph_without_s))
    W, ccs_without_s_without_w = split_w_and_rest(ccs_graph_without_s)

    handle_ccs(graph, W, T, D, S, ccs_without_s_without_w, color_dict)

    # Leftover W
    for w in W:
        handle_trivial_w(graph, w, S, color_dict)

    for _, list_colors in color_dict.items():
        assert len(list_colors) <= 2

    colors = color_remaining_nodes(graph, color_dict)

    # TODO enumerate colorings for the connected components that have more than one neighbor in a T[i]
    # TODO get non-trivial components and remove colors
    return colors
