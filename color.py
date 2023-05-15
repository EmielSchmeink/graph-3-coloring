import os
import sys

import networkx as nx

from graph_coloring.generic.csp.solve import csp_solve
from graph_coloring.generic.dsatur.solve import dsatur_solve
from graph_coloring.generic.sat.solve import sat_solve
from graph_coloring.non_generic.locally_connected.solve import locally_connected_solve
from graph_coloring.non_generic.p7_c3.solve import p7_c3_solve
from graph_coloring.non_generic.planar_triangle_free.solve import planar_solve
from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_drawer import draw_graph_with_color_from_dict, draw_graph


def draw_and_check_coloring(graph, colors):
    draw_graph_with_color_from_dict(graph, colors)

    GraphChecker().valid_3_coloring(graph, colors)


def color_locally_connected(graph):
    original_graph = graph.copy()
    colors = locally_connected_solve(graph)

    if colors is not None:
        draw_and_check_coloring(original_graph, colors)
        return True
    return False


def color_sat(graph):
    original_graph = graph.copy()
    colors = sat_solve(graph)

    if colors is not None:
        draw_and_check_coloring(original_graph, colors)
        return True
    return False


def color_planar(graph):
    original_graph = graph.copy()
    colors = planar_solve(graph)

    if colors is not None:
        draw_and_check_coloring(original_graph, colors)
        return True
    return False


def color_p7_c3(graph):
    original_graph = graph.copy()
    colors = p7_c3_solve(graph)

    if colors is not None:
        draw_and_check_coloring(original_graph, colors)
        return True
    return False


def color_csp(graph):
    original_graph = graph.copy()
    colors = csp_solve(graph)

    if colors is not None:
        draw_and_check_coloring(original_graph, colors)
        return True
    return False


def color_dsatur(graph):
    colors = dsatur_solve(graph)

    if colors is not None:
        draw_and_check_coloring(graph, colors)


def match_graph_type(graph_type_to_color):
    graph = nx.read_adjlist(f"graphs/{graph_path}")

    print(f"Coloring graph {graph_path}")
    draw_graph(graph, None)
    print(f"Finished drawing {graph_path}")

    sat_graph = graph.copy()
    csp_graph = graph.copy()

    sat_colorable = color_sat(sat_graph)
    csp_colorable = color_csp(csp_graph)

    match graph_type_to_color:
        case 'planar':
            planar_graph = graph.copy()
            planar_colorable = color_planar(planar_graph)
            assert planar_colorable == sat_colorable
        case 'locally_connected':
            locally_connected_graph = graph.copy()
            locally_connected_colorable = color_locally_connected(locally_connected_graph)
            assert locally_connected_colorable == sat_colorable
        case 'p7_c3':
            p7_c3_graph = graph.copy()
            p7_c3_colorable = color_p7_c3(p7_c3_graph)
            assert p7_c3_colorable == sat_colorable
        case _:
            print('Type not found...')

    assert csp_colorable == sat_colorable


if __name__ == '__main__':
    graph_type = sys.argv[1]

    for graph_path in os.listdir('graphs'):
        match_graph_type(graph_type)
