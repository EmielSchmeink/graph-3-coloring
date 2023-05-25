import os
import time

import networkx as nx

from graph_coloring.exceptions import InvalidGraphException
from graph_coloring.generic.csp.solve import csp_solve
from graph_coloring.generic.sat.solve import sat_solve
from graph_coloring.misc import write_results, convert_path_to_dict
from graph_coloring.non_generic.locally_connected.solve import locally_connected_solve
from graph_coloring.non_generic.p7_c3.solve import p7_c3_solve
from graph_coloring.non_generic.planar_triangle_free.solve import planar_solve
from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_drawer import draw_graph_with_color_from_dict, draw_graph


def draw_and_check_coloring(graph, colors):
    draw_graph_with_color_from_dict(graph, colors)
    GraphChecker().valid_3_coloring(graph, colors)


def color_graph(graph, graph_name, method):
    original_graph = graph.copy()

    start_time = time.time()
    match method:
        case 'sat':
            colors = sat_solve(graph, graph_name)
        case 'csp':
            colors = csp_solve(graph)
        case 'planar':
            colors = planar_solve(graph)
        case 'locally_connected':
            colors = locally_connected_solve(graph)
        case 'p7_c3':
            colors = p7_c3_solve(graph)
        case _:
            raise InvalidGraphException('Type not found...')

    total_time = time.time() - start_time
    print(f"Execution took {total_time} seconds")

    write_results(graph_name, method, total_time)

    if colors is not None:
        draw_and_check_coloring(original_graph, colors)
        return True
    return False


def match_graph_type(path):
    graph_dict = convert_path_to_dict(path)
    graph = nx.read_adjlist(f"graphs/{path}")

    print(f"Coloring graph {path}")
    draw_graph(graph, None)
    print(f"Finished drawing {path}")

    sat_graph = graph.copy()
    csp_graph = graph.copy()

    sat_colorable = color_graph(sat_graph, path, 'sat')
    csp_colorable = color_graph(csp_graph, path, 'csp')

    graph_type_colorable = color_graph(graph, path, graph_dict['graph_type'])
    assert graph_type_colorable == sat_colorable
    assert csp_colorable == sat_colorable


if __name__ == '__main__':
    for graph_path in os.listdir('graphs'):
        match_graph_type(graph_path)
