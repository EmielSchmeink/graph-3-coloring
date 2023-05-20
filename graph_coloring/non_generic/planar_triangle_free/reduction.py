import networkx as nx

from graph_coloring.exceptions import InvalidMultigramException
from graph_coloring.non_generic.planar_triangle_free.safety import check_if_k_4_is_octagram, check_if_k_5_is_pentagram, \
    get_distinct_neighbors, check_if_k_5_is_decagram


def identify_vertices(graph: nx.Graph, first_node, second_node):
    """
    Identify the vertices from the given multigram, according to the reduction rules.
    :param graph: The graph where to execute the identification in
    :param second_node: The first node to be identified, and the node that will be relabeled
    :param first_node: The second node to be identified
    :return: The graph with the identified node
    """
    identified_graph = nx.contracted_nodes(graph, first_node, second_node, self_loops=False)
    identified_graph = nx.relabel_nodes(identified_graph, {first_node: f"{first_node}_{second_node}"})
    return identified_graph


def multigram_reduction(multigram_tuple, graph):
    """
    Reduce the given graph using the given multigram, according to the reduction rules.
    :param multigram_tuple: The safe multigram to be reduced
    :param graph: The graph where to execute the reduction in
    :return: The graph with the reduced multigram
    """
    multigram = multigram_tuple[0]
    match len(multigram):
        case 1:
            graph.remove_nodes_from(multigram)
            return graph
        case 4:
            if check_if_k_4_is_octagram(multigram, graph):
                graph.remove_nodes_from(multigram)
                return graph
            else:
                return identify_vertices(graph, multigram[0], multigram[2])
        case 5:
            if check_if_k_5_is_decagram(multigram, graph):
                distinct_neighbors = get_distinct_neighbors(multigram, graph)
                graph.remove_nodes_from(multigram)

                graph.add_edge(distinct_neighbors[0], distinct_neighbors[2])
                return graph
            elif check_if_k_5_is_pentagram(multigram, graph):
                distinct_neighbors = get_distinct_neighbors(multigram, graph)
                graph.remove_nodes_from(multigram[0:4])

                identify_1 = identify_vertices(graph, distinct_neighbors[1], multigram[4])
                identify_2 = identify_vertices(identify_1, distinct_neighbors[2], distinct_neighbors[3])

                return identify_2
            else:
                # This is not supposed to happen
                raise InvalidMultigramException('This is not supposed to happen, '
                                                'at this stage the multigram has to be a safe pentragram or decagram.')
        case 6:
            return identify_vertices(graph, multigram[0], multigram[2])

    raise InvalidMultigramException
