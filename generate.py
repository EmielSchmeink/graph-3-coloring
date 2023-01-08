from graph_coloring.sat import sat_solve
from graph_coloring.dsatur import dsatur_solve
from graph_coloring.exceptions import InvalidColoringException
from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_drawer import draw_graph
from graph_generation.graph_generator import GraphGenerator

graph_generator = GraphGenerator(checker=GraphChecker)

configurations = [
    # [0.3, None, 3, True, None],
    # [0.5, None, 3, True, None],
    # [0.8, None, 3, True, None],
    # [0.3, 4, 5, None, None],
    # [0.5, 4, 5, None, None],
    [0.8, 4, 5, None, None],
    # [0.3, 7, 3, None, None],
    # [0.5, 7, 3, None, None],
    # [0.8, 7, 3, None, None],
]


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


for config in configurations:
    for n in [1000]:
        g = graph_generator.find_graphs_with_conditions(n, config[0], config[1], config[2], config[3], config[4])
