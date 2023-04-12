from graph_coloring.generic.csp.bushy_forest import get_maximal_bushy_forest
from graph_coloring.generic.csp.csp_sat import csp_satisfier
from graph_coloring.generic.csp.k13 import *


def find_vertices_in_cycles(graph):
    """
    Get all vertices with degree 3 in a cycle.
    :param graph: Graph of degree 3 vertices
    :return: List of cycles with degree 3 vertices
    """
    graph_cycles = []
    cycles_found = True

    try:
        graph_3_unfrozen = graph.copy()
        # TODO bit hacky, exits while when find_cycle fails to find a cycle, not in a nice way
        while cycles_found:
            # draw_graph(graph_3_unfrozen, None)

            found_cycle = nx.find_cycle(graph_3_unfrozen)
            unique_vertices = set(list(sum(found_cycle, ())))
            graph_cycles.append(unique_vertices)
            graph_3_unfrozen.remove_nodes_from(unique_vertices)
    except nx.NetworkXNoCycle:
        pass

    return graph_cycles


def create_color_dict_for_nodes(nodes):
    """
    Get dict of all colors for the given nodes.
    :param nodes: List of nodes to be added to the dict
    :return: Dict of node: color pairs
    """
    return {node: ['red', 'green', 'blue'] for node in nodes}


def get_all_vertices(bushy_forest, k13_list, graph_without_forest_neighbors_k13, graph_complete):
    """
    Get all vertices from the bushy forest, the K1,3s and the remaining vertices in the graph.
    :param bushy_forest: The maximal bushy forest
    :param k13_list: A list of K13s
    :param graph_without_forest_neighbors_k13: The remaining vertices in the graph
    :param graph_complete: The original graph
    :return: List of all vertices from the bushy forest, the K1,3s and the remaining vertices in the graph
    """
    all_vertices = []

    for tree in bushy_forest:
        all_vertices.extend(tree.get_all_nodes_and_neighbors(graph_complete))

    for k13 in k13_list:
        all_vertices.append(k13.center)
        all_vertices.extend(k13.neighbors)
        all_vertices.extend(k13.tree_grandchildren)

    all_vertices.extend(list(graph_without_forest_neighbors_k13.nodes))

    return list(set(all_vertices))


def get_all_vertices_to_be_colored(bushy_forest, k13_list, graph_without_forest_neighbors_k13, graph_complete):
    """
    Get all vertices that will need coloring in SAT, so the bushy forest leaves and neighbors,
    the K13 children and grandchildren, and the remaining vertices in the graph.
    :param bushy_forest: The maximal bushy forest
    :param k13_list: A list of K13s
    :param graph_without_forest_neighbors_k13: The remaining vertices in the graph
    :param graph_complete: The original graph
    :return: List of vertices that need to be colored in SAT
    """
    all_vertices = []

    for tree in bushy_forest:
        all_vertices.extend(tree.leaves)
        all_vertices.extend(tree.get_neighbor_vertices(graph_complete))

    for k13 in k13_list:
        all_vertices.extend(k13.neighbors)
        all_vertices.extend(k13.tree_grandchildren)

    all_vertices.extend(list(graph_without_forest_neighbors_k13.nodes))

    return list(set(all_vertices))


def recurrence_coloring(L, children_dict, color_dict, remaining_graph, vertices_to_be_colored):
    """
    Recursively color the root and internal nodes of the bushy forest + K13 centers, and check if the remaining colors
    for the vertices to be colored results in a valid coloring output by SAT, or if it fails to color try all other
    options, until all options have been exhausted. If all options exhausted, indicate that no coloring is possible.
    :param L: List of vertices to be given a fixed coloring
    :param children_dict: Dict containing the children for all nodes
    :param color_dict: Dict containing the available colors for all nodes
    :param remaining_graph: Graph induced by all remaining vertices after removing the bushy forest and K13s
    :param vertices_to_be_colored: The vertices that still need coloring by SAT
    :return: Dict containing a valid coloring for all remaining vertices and nodes in L
    """
    if len(L) == 0:
        to_be_colored_dict = {}

        for v in vertices_to_be_colored:
            to_be_colored_dict[v] = color_dict[v]

        csp_colors = csp_satisfier(remaining_graph, to_be_colored_dict)

        if csp_colors is None:
            return None

        for node, color in csp_colors.items():
            color_dict[node] = color

        return color_dict
    else:
        x = L.pop(0)

        allowed_colors_for_x = color_dict[x]

        for color in allowed_colors_for_x:
            temp_color_dict = color_dict.copy()
            temp_color_dict[x] = color

            for child in children_dict[x]:
                # Get the current allowed colors for the child
                if type(temp_color_dict[child]) is not str:
                    child_colors = temp_color_dict[child].copy()
                else:
                    child_colors = temp_color_dict[child]

                    # If there is only 1 color the child can be colored with, and it is the same as the parent
                    # Then this is an invalid coloring, so we can stop checking
                    if color == child_colors:
                        return None

                # Remove the parent color as a possible color
                if color in child_colors:
                    child_colors.remove(color)

                temp_color_dict[child] = child_colors

            # Copy the list of remaining nodes to make sure that if the recursion starts here again
            # after failing downstream, we know which nodes still need to be colored
            L_copy = L.copy()
            z3_output = recurrence_coloring(L_copy,
                                            children_dict,
                                            temp_color_dict,
                                            remaining_graph,
                                            vertices_to_be_colored)

            if z3_output is not None:
                return z3_output

        # Indicate that using the allowed colors for x does not result into a valid coloring
        # Use different allowed colors and check again
        return None


def get_colorings(bushy_forest, k13_list, graph_without_forest_neighbors_k13, graph_complete):
    """
    Setup and get the recursive coloring for the graph.
    :param bushy_forest: The maximal bushy forest
    :param k13_list: A list of K13s
    :param graph_without_forest_neighbors_k13: The remaining vertices in the graph
    :param graph_complete: The original graph
    :return: Dict containing a valid coloring for all remaining vertices and nodes in L
    """
    L = []
    node_children = {}
    for tree in bushy_forest:
        node_children = node_children | tree.get_node_children_dict()
        L.append(tree.root)
        L.extend(tree.internal_nodes)

    for k13 in k13_list:
        node_children = node_children | k13.get_children_dict()
        L.append(k13.center)

    all_vertices = get_all_vertices(bushy_forest, k13_list, graph_without_forest_neighbors_k13, graph_complete)
    all_vertices_to_be_colored = get_all_vertices_to_be_colored(bushy_forest,
                                                                k13_list,
                                                                graph_without_forest_neighbors_k13,
                                                                graph_complete)

    color_dict = create_color_dict_for_nodes(all_vertices)

    remaining_graph = nx.subgraph(graph_complete, all_vertices_to_be_colored)
    colors = recurrence_coloring(L, node_children, color_dict, remaining_graph, all_vertices_to_be_colored)

    return colors


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


def csp_solve(graph: nx.Graph):
    """
    Get a 3-coloring for the given graph, or indicate that a 3-coloring is not possible, using the CSP algorithm
    presented in the paper by Richard Beigel and David Eppstein. 3-coloring in time O(1.3289ˆn).
    Journal of Algorithms, 54(2):168–204, 2 2005. ISSN 01966774. doi:10.1016/j.jalgor.2004.06.008.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes, or None
    """
    graph_complete = graph.copy()

    # Step 1: If the degree is lower than 3, we want to remove it from the graph
    low_degree_vertices = [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] <= 2]
    graph.remove_nodes_from(low_degree_vertices)

    # Step 2.1: Remove the cycles with degree 3, and later recursively color them
    # TODO these must be induced cycles
    # degree_3_vertices = get_vertices_of_degree_n(graph, 3)
    # graph_3: nx.Graph = graph.subgraph(degree_3_vertices)
    # graph_3_cycle_vertices = find_vertices_in_cycles(graph_3)
    #
    # for cycle in graph_3_cycle_vertices:
    #     graph.remove_nodes_from(cycle)

    # Step 2.2: Remove the trees with more than 8 vertices, and later recursively color them
    # TODO handle these later
    # degree_3_vertices_without_cycles = get_vertices_of_degree_n(graph, 3)
    # graph_3_without_cycle = graph.subgraph(degree_3_vertices_without_cycles)
    # graph_3_cc = [component for component in nx.connected_components(graph_3_without_cycle)]
    # graph_3_cc_8 = []
    #
    # for component in graph_3_cc:
    #     if len(component) >= 8:
    #         graph_3_cc_8.append(component)
    #         graph.remove_nodes_from(component)

    # Step 3:
    bushy_forest = get_maximal_bushy_forest(graph)

    bushy_forest_vertices = []
    for tree in bushy_forest:
        bushy_forest_vertices.extend(tree.get_all_nodes())

    # Step 4:
    graph_with_forest = graph.copy()
    graph_without_forest = graph.copy()
    graph_without_forest.remove_nodes_from(bushy_forest_vertices)

    k13_list = get_maximal_set_of_k13(graph_without_forest)

    # Remove the K1,3s from the graph without the forest
    graph_without_k13 = graph_without_forest.copy()

    for k13 in k13_list:
        k13.remove_k13_from_graph(graph_without_k13)

    # Step 5
    optimized_k13_list = optimize_k13_list(graph_without_k13, k13_list)

    # Step 6
    graph_without_forest_neighbors_k13 = graph_with_forest.copy()
    forest_vertices_with_neighbors = []
    forest_vertices_with_neighbors.extend(bushy_forest_vertices)

    for tree in bushy_forest:
        forest_vertices_with_neighbors.extend(tree.neighbors)

    max_flow_graph = create_flow_graph(optimized_k13_list)
    k13_list_with_gc = assign_flow_vertices_to_k13(k13_list, max_flow_graph)

    for k13 in k13_list_with_gc:
        k13.remove_k13_from_graph(graph_without_forest_neighbors_k13)

        graph_without_forest_neighbors_k13.remove_nodes_from(k13.get_k13_grandchildren())

    graph_without_forest_neighbors_k13.remove_nodes_from(forest_vertices_with_neighbors)

    # Step 7
    colors_dict = get_colorings(bushy_forest, k13_list_with_gc, graph_without_forest_neighbors_k13, graph)

    if colors_dict is None:
        print('CSP: No 3-coloring possible!')
        return None

    # Color the low degree vertices, cycles and large components efficiently
    for low_degree_vertex in low_degree_vertices:
        neighbors = list(nx.neighbors(graph_complete, low_degree_vertex))
        possible_colors = get_possible_colors(neighbors, colors_dict)
        colors_dict[low_degree_vertex] = possible_colors[0]

    # for degree_3_cycle in graph_3_cycle_vertices:
    #     for vertex in degree_3_cycle:
    #         neighbors = [neighbor for neighbor in nx.neighbors(graph_complete, vertex)]
    #         possible_colors = get_possible_colors(neighbors, colors)
    #
    #         # TODO will fail sometimes due to having a 3 cycle with 2 or more colors already used by neighbors
    #         colors.append((vertex, possible_colors[0]))

    print('CSP: 3-coloring possible...')
    return colors_dict
