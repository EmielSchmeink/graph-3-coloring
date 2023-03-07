from dataclasses import dataclass

import networkx as nx

from graph_coloring.exceptions import sanity_check_coloring, InvalidColoringException
from graph_generation.graph_drawer import draw_graph, color_edges


def find_vertices_in_cycle(graph):
    graph_cycles = []
    cycles_found = True

    try:
        graph_3_unfrozen = graph.copy()
        # TODO bit hacky, exits while when find_cycle fails to find a cycle, not in a nice way
        while cycles_found:
            draw_graph(graph_3_unfrozen, None)

            found_cycle = nx.find_cycle(graph_3_unfrozen)
            unique_vertices = set(list(sum(found_cycle, ())))
            graph_cycles.append(unique_vertices)
            graph_3_unfrozen.remove_nodes_from(unique_vertices)
    except nx.NetworkXNoCycle:
        pass

    return graph_cycles


def get_vertices_of_degree_n(graph, n, at_least=False):
    if at_least:
        return [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] >= n]

    return [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] == n]


def intersection(list1, list2):
    return list(set(list1) & set(list2))


def bushy_dfs(graph, bushy_forest_vertices, possible_forest_vertices):
    if len(possible_forest_vertices) == 0:
        return bushy_forest_vertices

    new_bushy_forest_vertices = []
    new_possible_forest_vertices = []

    vertex = possible_forest_vertices.pop(0)
    neighbors = [v for v in graph.neighbors(vertex)]
    neighbors_in_forest = intersection(bushy_forest_vertices, neighbors)
    neighbors_not_in_forest = [neighbor for neighbor in neighbors if neighbor not in neighbors_in_forest]

    if not len(neighbors) >= 4:
        new_bushy_forest_vertices.append(vertex)
        return new_bushy_forest_vertices

    if len(neighbors_in_forest) <= 1:
        new_bushy_forest_vertices.append(vertex)
        new_bushy_forest_vertices.extend(neighbors)
        new_possible_forest_vertices.extend(possible_forest_vertices)
        new_possible_forest_vertices.extend(neighbors)

        test = bushy_dfs(graph, new_bushy_forest_vertices, new_possible_forest_vertices).copy()
        bushy_forest_vertices.extend(neighbors_not_in_forest)
        bushy_forest_vertices.extend(test)

    return bushy_forest_vertices


def get_maximal_bushy_forest(graph):
    graph_copy = graph.copy()
    degree_4_vertices = get_vertices_of_degree_n(graph_copy, 4, True)

    possible_forest_vertices = [degree_4_vertices[0]]

    bushy_forest_vertices = bushy_dfs(graph_copy, [], possible_forest_vertices)

    # bushy_forest = nx.subgraph(graph, bushy_forest_vertices)
    # maximal_bushy_forest_vertices = [vertex_degree[0] for vertex_degree in bushy_forest.degree if vertex_degree[1] > 0]
    #
    # test = nx.subgraph(graph, maximal_bushy_forest_vertices)
    #
    # draw_graph(test, None)

    return [degree_4_vertices[0]]


@dataclass
class K13:
    """Class representing a K1,3 instance."""
    center: str
    neighbors: list
    neighbors_edges: list

    def check_if_k13_exists(self, graph: nx.Graph):
        if len(self.neighbors) != 3:
            raise Exception('A K1,3 must contain exactly 3 neighbors.')

        return graph.has_node(self.center) \
            and graph.has_node(self.neighbors[0]) \
            and graph.has_node(self.neighbors[1]) \
            and graph.has_node(self.neighbors[2])

    def get_k13_edges(self):
        return [(self.center, neighbor) for neighbor in self.neighbors]

    def remove_k13_from_graph(self, graph: nx.Graph):
        graph.remove_node(self.center)
        graph.remove_nodes_from(self.neighbors)

    def add_k13_to_graph(self, graph: nx.Graph):
        graph.add_node(self.center)
        graph.add_nodes_from(self.neighbors)
        graph.add_edges_from(self.get_k13_edges())
        graph.add_edges_from(self.neighbors_edges)


def get_maximal_set_of_k13(graph, forbidden_centers=None):
    if forbidden_centers is None:
        forbidden_centers = []

    graph_without_maximal_k13 = graph.copy()

    degree_3 = get_vertices_of_degree_n(graph_without_maximal_k13, 3)

    k13_list = []

    for vertex in degree_3:
        if vertex in forbidden_centers:
            continue

        # If the vertex was already removed by another K1,3 we skip it
        if graph_without_maximal_k13.has_node(vertex):
            neighbors = [v for v in nx.neighbors(graph_without_maximal_k13, vertex)]
        else:
            continue

        # If one of the neighbors was already removed, we skip the center vertex
        if len(neighbors) != 3:
            continue

        neighbor_edges = []

        for neighbor in neighbors:
            neighbor_edges.extend(graph.edges([neighbor]))

        possible_k13 = K13(vertex, neighbors, neighbor_edges)

        # TODO this should not matter
        # if not possible_k13.check_if_k13_exists(graph_without_maximal_k13):
        #     continue

        # Save this K1,3 and remove it from the graph
        k13_list.append(possible_k13)
        possible_k13.remove_k13_from_graph(graph_without_maximal_k13)

    return k13_list


def draw_k13_list(graph, k13_list):
    edges = []

    for k13 in k13_list:
        edges.extend(k13.get_k13_edges())

    draw_graph(graph, None, edge_colors=color_edges(graph, edges))


def csp_solve(graph: nx.Graph):
    """
    1. if the input graph G contains any vertex v with degree less than two, recursively
    color G \ {v} and assign v a color different from its neighbors (Lemma 20).
    2. If the input graph contains a cycle or large tree of degree-three vertices, split the
    problem into smaller instances according to Lemmas 21 and 22, recursively attempt
    to color each smaller instance, and return the first successful coloring found by these
    recursive calls.
    3. Find a maximal bushy forest F in G (Lemma 23).
    4. Find a maximal set T of K1,3 subgraphs in G \ F .
    5. While it is possible to increase the size of T by removing one K1,3 subgraph and
    using the vertices in G \ (F ∪ T ) to form two more K1,3 subgraphs, do so.
    6. Use the network flow algorithm of Lemma 25 to assign the vertices of G \ (F ∪
    N (F ) ∪ T ) to trees in T , forming a forest H of height-two trees.
    7. Recursively search through all consistent combinations of colors for the bushy forest
    roots and internal nodes, and for selected vertices in H as described in Lemma 26.
    For each coloring of these vertices, form a (3, 2)-CSP instance describing the pos-
    sible colorings of the uncolored vertices, and use our CSP algorithm to attempt to
    solve this instance. If one of the CSP instances is solvable, return the resulting col-
    oring. If no CSP instance is solvable, return a flag value indicating that no coloring
    exists.
    :param graph:
    :return:
    """
    graph_complete = graph.copy()
    draw_graph(graph, None)

    # Step 1: If the degree is lower than 3, we want to remove it from the graph
    low_degree_vertices = [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] <= 2]
    graph.remove_nodes_from(low_degree_vertices)

    # Step 2.1: Remove the cycles with degree 3, and later recursively color them
    degree_3_vertices = get_vertices_of_degree_n(graph, 3)
    graph_3: nx.Graph = graph.subgraph(degree_3_vertices)
    graph_3_cycle_vertices = find_vertices_in_cycle(graph_3)

    for cycle in graph_3_cycle_vertices:
        graph.remove_nodes_from(cycle)

    # Step 2.2: Remove the trees with more than 8 vertices, and later recursively color them
    degree_3_vertices_without_cycles = get_vertices_of_degree_n(graph, 3)
    graph_3_without_cycle = graph.subgraph(degree_3_vertices_without_cycles)
    graph_3_cc = [component for component in nx.connected_components(graph_3_without_cycle)]

    for component in graph_3_cc:
        if len(component) >= 8:
            graph.remove_nodes_from(component)

    # Step 3:
    draw_graph(graph, None)
    bushy_forest_vertices = get_maximal_bushy_forest(graph)

    # TODO make it an actual bushy forest
    test = nx.subgraph(graph, bushy_forest_vertices)
    draw_graph(test, None)

    # Step 4:
    graph_with_forest = graph.copy()
    graph_without_forest = graph.copy()
    graph_without_forest.remove_nodes_from(bushy_forest_vertices)

    k13_list = get_maximal_set_of_k13(graph_without_forest)
    draw_k13_list(graph_without_forest, k13_list)

    # Remove the K1,3s from the graph without the forest
    graph_without_k13 = graph_without_forest.copy()

    for k13 in k13_list:
        k13.remove_k13_from_graph(graph_without_k13)
    draw_graph(graph_without_k13, None)

    # Step 5
    # TODO loop over K1,3 list and check if we can create more by removing one
    for k13 in k13_list:
        k13.add_k13_to_graph(graph_without_k13)
        draw_graph(graph_without_k13, None)
        new_k13_list = get_maximal_set_of_k13(graph_without_k13)
        # TODO should we remove the K1,3 from T or the graph? Should it be a K1,3 in G \ F or in G \ (F u T)?
        test = 0

    draw_graph(graph, None)

    colors = []

    try:
        sanity_check_coloring(graph, colors)
        print('CSP: 3-coloring possible...')
    except InvalidColoringException:
        print('CSP: No 3-coloring possible!')
        return None

    return colors
