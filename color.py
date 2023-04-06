import os

import networkx as nx

from graph_coloring.generic.csp.csp import csp_solve
from graph_coloring.generic.dsatur import dsatur_solve
from graph_coloring.generic.sat import sat_solve
from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_drawer import draw_graph_with_color_from_dict, draw_graph


def draw_and_check_coloring(graph, colors):
    draw_graph_with_color_from_dict(graph, colors)

    GraphChecker().valid_3_coloring(graph, colors)


def color_sat(graph):
    colors = sat_solve(graph)

    if colors is not None:
        draw_and_check_coloring(graph, colors)
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


for graph_path in os.listdir('graphs'):
    graph = nx.read_adjlist(f"graphs/{graph_path}")

    print(f"Coloring graph {graph_path}")
    draw_graph(graph, None)
    csp_graph = graph.copy()
    sat_graph = graph.copy()
    csp_colorable = color_csp(csp_graph)
    sat_colorable = color_sat(sat_graph)
    assert csp_colorable == sat_colorable

    # color_dsatur(graph)
