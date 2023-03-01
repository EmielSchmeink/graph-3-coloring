import networkx as nx

from graph_coloring.exceptions import sanity_check_coloring, InvalidColoringException
from graph_generation.graph_drawer import draw_graph


def find_vertices_in_cycle(graph):
    graph_cycles = []
    cycles_found = True

    try:
        graph_3_unfrozen = graph.copy()
        # TODO bit hacky, exists while when find_cycle fails to find a cycle, not in a nice way
        while cycles_found:
            draw_graph(graph_3_unfrozen, None)

            found_cycle = nx.find_cycle(graph_3_unfrozen)
            unique_vertices = set(list(sum(found_cycle, ())))
            graph_cycles.append(unique_vertices)
            graph_3_unfrozen.remove_nodes_from(unique_vertices)
    except nx.NetworkXNoCycle:
        pass

    return graph_cycles


def get_vertices_of_degree_n(graph, n):
    return [vertex_degree[0] for vertex_degree in graph.degree if vertex_degree[1] == n]


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

    # Step 2: Remove the cycles with degree 3, and later recursively color them
    degree_3_vertices = get_vertices_of_degree_n(graph, 3)
    graph_3: nx.Graph = graph.subgraph(degree_3_vertices)
    graph_3_cycle_vertices = find_vertices_in_cycle(graph_3)

    for cycle in graph_3_cycle_vertices:
        graph.remove_nodes_from(cycle)

    # Step 3: Remove the trees with more than 8 vertices, and later recursively color them
    degree_3_vertices_without_cycles = get_vertices_of_degree_n(graph, 3)
    graph_3_without_cycle = graph.subgraph(degree_3_vertices_without_cycles)
    graph_3_cc = [component for component in nx.connected_components(graph_3_without_cycle)]

    for component in graph_3_cc:
        if len(component) >= 8:
            graph.remove_nodes_from(component)

    # Step 4:


    draw_graph(graph, None)

    colors = []

    try:
        sanity_check_coloring(graph, colors)
        print('CSP: 3-coloring possible...')
    except InvalidColoringException:
        print('CSP: No 3-coloring possible!')
        return None

    return colors
