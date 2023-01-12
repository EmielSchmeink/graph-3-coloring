import os

import networkx as nx

from graph_coloring.dsatur import dsatur_solve
from graph_coloring.exceptions import InvalidColoringException
from graph_coloring.sat import sat_solve
from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_drawer import draw_graph


def draw_and_check_coloring(graph, colors):
    draw_graph(graph, colors)

    if not GraphChecker().valid_3_coloring(graph, colors):
        raise InvalidColoringException


def color_sat(graph):
    colors = sat_solve(graph)

    if colors is not None:
        draw_and_check_coloring(graph, colors)


def color_dsatur(graph):
    colors = dsatur_solve(graph)

    if colors is not None:
        draw_and_check_coloring(graph, colors)


for graph_path in os.listdir('graphs'):
    graph = nx.read_adjlist(f"graphs/{graph_path}")
    color_sat(graph)
    color_dsatur(graph)
