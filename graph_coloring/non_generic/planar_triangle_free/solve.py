import networkx as nx

from graph_coloring.exceptions import InvalidGraphException
from graph_coloring.misc import get_vertices_of_degree_n
from graph_coloring.non_generic.planar_triangle_free.coloring import convert_multigrams_into_coloring
from graph_coloring.non_generic.planar_triangle_free.reduction import multigram_reduction
from graph_coloring.non_generic.planar_triangle_free.safety import check_multigram_safety


def get_multigram(embedding, graph):
    """
    Greedily get a multigram by first checking for low degree vertices,
    and if none are found, get a multigram by walking over a face and checking if it contains a multigram,
    until a multigram is found (there has to be one).
    :param embedding: Planar embedding to walk over faces
    :param graph: Graph to check for safety in and for finding low degree vertices
    :return: The multigram vertices, and the type
    """
    low_degree_vertices = get_vertices_of_degree_n(graph, 2, up_to=True)
    if len(low_degree_vertices) > 0:
        return [low_degree_vertices[0]], 'monogram'

    _, embedding = nx.check_planarity(graph)
    embedding.check_structure()

    for first_vertex in embedding.nodes:
        # Greedily get the first multigram
        cw_neighbor = list(embedding.neighbors_cw_order(first_vertex))[0]

        multigram = embedding.traverse_face(first_vertex, cw_neighbor)
        safe, multigram_type = check_multigram_safety(multigram, graph)
        if safe:
            return multigram, multigram_type

    raise InvalidGraphException


def planar_solve(graph: nx.Graph):
    """
    Get a 3-coloring for the given planar triangle-free graph, using the algorithm
    presented in the paper by Zdenek Dvorak, Ken-ichi Kawarabayashi, and Robin Thomas.
    Three-coloring triangle-free planar graphs in linear time. ACM Transactions
    on Algorithms 7 (2011), Article 41, 2 2013. doi: 10.48550/arxiv.1302.5121.
    URL https://arxiv.org/abs/1302.5121v1.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes
    """
    # Create the embedding and sanity check that the graph is actually planar
    embedding: nx.PlanarEmbedding
    planarity, embedding = nx.check_planarity(graph)
    embedding.check_structure()
    assert planarity is True

    temp_embedding = embedding.copy()
    temp_graph = graph.copy()
    multigram_found = True
    multigrams = []
    while multigram_found:
        if len(list(temp_graph.nodes)) == 0:
            break

        multigram = get_multigram(temp_embedding, temp_graph)
        multigrams.append(multigram)
        temp_graph = multigram_reduction(multigram, temp_graph)

    color_dict = convert_multigrams_into_coloring(multigrams, graph)

    print('Planar Triangle-free: 3-coloring found...')
    return color_dict
