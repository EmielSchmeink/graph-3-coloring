import networkx as nx

from graph_coloring.exceptions import InvalidMultigramException
from graph_coloring.non_generic.planar_triangle_free.safety import check_if_k_4_is_octagram


def identify_vertices(graph: nx.Graph, multigram):
    """
    Identify the vertices from the given multigram, according to the reduction rules.
    :param graph: The graph where to execute the identification in
    :param multigram: Tetra- or hexagram to be reduced
    :return: The graph with the identified node
    """
    v_1 = multigram[0]
    v_3 = multigram[2]

    identified_graph = nx.contracted_nodes(graph, v_1, v_3, self_loops=False)
    identified_graph = nx.relabel_nodes(identified_graph, {v_1: f"{v_1}_{v_3}"})
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
                return identify_vertices(graph, multigram)
        case 5:
            # TODO reduce pentagrams
            assert False
        case 6:
            return identify_vertices(graph, multigram)

    raise InvalidMultigramException
