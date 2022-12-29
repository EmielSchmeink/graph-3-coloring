import networkx as nx
from graph_coloring.exceptions import sanity_check_coloring


def dsatur_solve(graph):
    # TODO as some point indices become strings instead of ints, handle that
    color_dict = nx.coloring.greedy_color(graph, strategy='DSATUR')

    colors = []

    for i in range(len(graph.nodes)):
        if color_dict[str(i)] == 0:
            colors.append('red')
        if color_dict[str(i)] == 1:
            colors.append('green')
        if color_dict[str(i)] == 2:
            colors.append('blue')

    sanity_check_coloring(graph, colors)

    return colors
