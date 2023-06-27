import itertools

import networkx as nx
from tqdm import tqdm

from graph_coloring.exceptions import InvalidGraphException
from graph_coloring.misc import intersection, get_vertices_of_degree_n


def get_triangle_from_neighbors(graph, vertex):
    """
    Greedily get a triangle from the neighbors of the given vertex.
    :param graph: Graph to get the triangle from
    :param vertex: Vertex as start of the triangle
    :return: Ordering of 3 vertices that make a triangle
    """
    neighbors = list(graph.neighbors(vertex))

    for neighbor_1 in neighbors:
        for neighbor_2 in neighbors:
            if neighbor_1 in graph.neighbors(neighbor_2) \
                    and neighbor_1 != neighbor_2:
                return [vertex, neighbor_1, neighbor_2]

    raise InvalidGraphException('This should not happen with a locally connected graph.')


def get_W(H):
    """
    Get the W partition of the bipartite H.
    :param H: The bipartite graph H
    :return: List of vertices in the set W
    """
    return [x for x, y in H.nodes(data=True) if y['bipartite'] == 'W']


def get_U(H):
    """
    Get the U partition of the bipartite H.
    :param H: The bipartite graph H
    :return: List of vertices in the set U
    """
    return [x for x, y in H.nodes(data=True) if y['bipartite'] == 'U']


def get_W_prime(H, graph, w):
    """
    Get W_i' as defined by N(w_i) ∩ W_i
    :param H: The bipartite graph with sets W and U
    :param graph: Graph to get the neighbors of w from
    :param w: The distinguished vertex from W
    :return: List of vertices as defined as W'
    """
    return intersection(graph.neighbors(w), get_W(H), sort=True)


def get_U_prime(H, graph, w):
    """
    Get U_i' as defined by N(w_i) ∩ U_i
    :param H: The bipartite graph with sets W and U
    :param graph: Graph to get the neighbors of w from
    :param w: The distinguished vertex from U
    :return: List of vertices as defined as U'
    """
    return intersection(list(graph.neighbors(w)), get_U(H), sort=True)


def get_v_i(H_prime, U_prime):
    """
    Greedily get v_i from U' where (v_i, v_i_prime) is and edge in H'
    :param H_prime: Graph to get v_i from
    :param U_prime: Set to get v_i_prime from
    :return: The node v_i
    """
    for v_i in U_prime:
        for v_i_prime in H_prime:
            # This should always be the case, but sanity check it regardless
            if H_prime.has_edge(v_i, v_i_prime):
                return v_i

    raise InvalidGraphException("I think this should not happen? Investigate")


def update_H(graph, v_i, V_i_1, H, W, U):
    """
    Update the graph H according to the following rules:

    For each x ∈ N(v_i):
    • If x /∈ Vi−1, add (x, v_i) to H_i; furthermore if x /∈ U_{i−1}, add x to U_i.
    • If x ∈ V_{i-1} (i.e., x ∈ W_{i−1}, delete edge (x, v_i) from H_i; furthermore if v_i is the only
    neighbor of x in H_{i−1}, delete x from W_i.
    If v_i has degree 0 in H_i after all these changes, delete v_i from H_i, otherwise move v_i from
    U_i to W_i.
    """
    neighbor_set = set(graph.neighbors(v_i))
    for x in neighbor_set:
        if x not in V_i_1:
            H.add_edge(x, v_i)

            # U_i-i and U_i are sets, so only unique elements can exist
            # If it wasn't there already we can add it regardless
            U.add(x)
        else:
            if list(H.neighbors(x)) == [v_i]:
                W.remove(x)

            H.remove_edge(x, v_i)

    if H.degree[v_i] == 0:
        H.remove_node(v_i)
    else:
        U.remove(v_i)
        W.append(v_i)


def update_H_prime(graph, v_i, H, W, H_prime, W_prime, U_prime, W_prime_i_1, U_prime_i_1):
    """
    Update the graph H' according to the following rules:

    If w_{i−1} ∈ V(H_i) (i.e., w_{i−1} ∈ W_i), then we set w_i = w_{i−1} and construct H′_i, W′i, U′i
    from H′_{i−1}, W′_{i-1}, U′_{i−1}, respectively, applying the following changes for each x ∈ N(v_i):
    • If x ∈ W′_{i−1}, delete (x, v_i) from H′_i; if x /∈ Wi, delete x from W′_i .
    • If x ∈ U′_{i−1}, add (x, v_i) to H′_i (in this case v_i ∈ V(H_i)).
    • If x /∈ W′_{i−1}, U′_{i−1}, no changes are made for x and (x, v_i)
    """
    for x in graph.neighbors(v_i):
        if x in W_prime_i_1:
            H_prime.remove_edge(x, v_i)

            if x not in W:
                W_prime.remove(x)
        if x in U_prime_i_1:
            H_prime.add_edge(x, v_i)

    if v_i not in list(H.nodes):
        H_prime.remove_node(v_i)
    else:
        U_prime.remove(v_i)
        W_prime.append(v_i)


def check_color_allowed(graph, node, color_dict):
    """
    Check if the current coloring creates an impossible coloring for the given node.
    :param graph: Graph to check coloring from
    :param node: Node that coloring is checked for
    :param color_dict: Dict containing the allowed colors
    :return: Bool whether it is allowed
    """
    neighbors = list(graph.neighbors(node))

    for neighbor in neighbors:
        allowed_colors = ['red', 'green', 'blue']
        neighbor_neighbors = list(graph.neighbors(neighbor))

        for nn in neighbor_neighbors:
            if nn in color_dict and color_dict[nn] in allowed_colors:
                allowed_colors.remove(color_dict[nn])

        if len(allowed_colors) == 0:
            return False

    return True


def color_using_ordering(graph, ordering):
    """
    Color the given graph using the given vertex ordering.
    :param graph: Graph to color
    :param ordering: Ordering to be used
    :return: Dict of colors or None
    """
    colors = {ordering[0]: 'red', ordering[1]: 'green', ordering[2]: 'blue'}

    for i in range(3, len(ordering)):
        v_i = ordering[i]
        neighbors = list(graph.neighbors(v_i))
        i_colors = ['red', 'green', 'blue']

        for subset in itertools.combinations(colors.items(), 2):
            u = subset[0][0]
            c_u = subset[0][1]
            v = subset[1][0]
            c_v = subset[1][1]

            # This is not a triangle
            if u not in list(graph.neighbors(v)):
                continue

            if u in neighbors and v in neighbors:
                if c_u == c_v:
                    return None
                if c_u in i_colors:
                    i_colors.remove(c_u)
                if c_v in i_colors:
                    i_colors.remove(c_v)

        if len(i_colors) > 0:
            temp_i_colors = i_colors.copy()
            for i_color in i_colors:
                temp_colors = colors.copy()
                temp_colors = temp_colors | {v_i: i_color}

                # Check if the current coloring creates a node with 3 different color neighbors
                # And if so, remove the color from the allowed list
                if check_color_allowed(graph, v_i, temp_colors):
                    colors = temp_colors
                    break
                else:
                    temp_i_colors.remove(i_color)

            # If the current node has no allowed colors anymore, a coloring is not possible
            if len(temp_i_colors) == 0:
                return None
        else:
            return None

    return colors


def locally_connected_solve(graph: nx.Graph):
    """
    Get a 3-coloring for the given locally connected graph, using the algorithm
    presented in the paper by Martin Kochol.
    Martin Kochol. 3-coloring and 3-clique-ordering of locally connected
    graphs. Journal of Algorithms, 54(1):122–125, 1 2005. ISSN 0196-6774.
    doi: 10.1016/J.JALGOR.2004.05.003.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes
    """
    low_degree_vertices = get_vertices_of_degree_n(graph, 0, up_to=True)
    low_degree_coloring = {node: 'red' for node in low_degree_vertices}
    graph.remove_nodes_from(low_degree_vertices)

    assert len(list(nx.connected_components(graph))) == 1

    # Get the initial V_3 with an arbitrary triangle (in this case just the first vertex)
    V = get_triangle_from_neighbors(graph, list(graph.nodes)[0])
    H = nx.Graph()
    for v in V:
        for neighbor in graph.neighbors(v):
            if neighbor in V:
                continue

            H.add_nodes_from([v], bipartite='W')
            H.add_nodes_from([neighbor], bipartite='U')
            H.add_edge(v, neighbor)

    # Get w_3 arbitrarily, so greedily the first element in W_i
    W = get_W(H)
    U = get_U(H)
    w = W[0]
    W_prime = get_W_prime(H, graph, w)
    U_prime = get_U_prime(H, graph, w)
    H_prime = nx.subgraph(H, W_prime + U_prime).copy()

    tqdm_nodes = tqdm(range(3, len(graph.nodes)))
    tqdm_nodes.set_description(desc="Creating 3-clique ordering", refresh=True)

    U = set(U)

    # Incrementally create a 3-clique ordering for the graph
    for _ in tqdm_nodes:
        # Save the previous iteration for later use
        w_i_1 = w
        W_prime_i_1 = W_prime.copy()
        U_prime_i_1 = U_prime.copy()

        # Get new v_i and update H accordingly
        v_i = get_v_i(H_prime, U_prime)
        update_H(graph, v_i, V, H, W, U)
        V.append(v_i)

        temp_color_dict = color_using_ordering(graph, V)

        if temp_color_dict is None:
            print('Locally Connected: No 3-coloring possible!\n')
            return None

        if len(V) == len(graph.nodes):
            break

        if w_i_1 in W:
            w = w_i_1
            update_H_prime(graph, v_i, H, W, H_prime, W_prime, U_prime, W_prime_i_1, U_prime_i_1)
        else:
            for vertex in W:
                if w != vertex:
                    w = vertex

            W_prime = intersection(graph.neighbors(w), W, sort=True)
            U_prime = intersection(graph.neighbors(w), U, sort=True)
            H_prime = nx.Graph()

            for u in U_prime:
                if u not in list(H.nodes()):
                    continue

                for u_neighbor in H.neighbors(u):
                    if u_neighbor not in W_prime:
                        continue

                    H_prime.add_nodes_from([u_neighbor], bipartite='W')
                    H_prime.add_nodes_from([u], bipartite='U')
                    H_prime.add_edge(u_neighbor, u)

    color_dict = color_using_ordering(graph, V)

    if color_dict is None:
        print('Locally Connected: No 3-coloring possible!')
        return None

    print('Locally Connected: 3-coloring possible')
    return color_dict | low_degree_coloring
