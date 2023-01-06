import networkx as nx
from graph_coloring.exceptions import sanity_check_coloring, InvalidColoringException


def dsatur_solve(graph):
    color_dict = nx.coloring.greedy_color(graph, strategy='DSATUR')

    colors = []

    if type(list(color_dict.keys())[0]) is str:
        for i in range(len(graph.nodes)):
            if color_dict[str(i)] == 0:
                colors.append('red')
            if color_dict[str(i)] == 1:
                colors.append('green')
            if color_dict[str(i)] == 2:
                colors.append('blue')
    else:
        for i in range(len(graph.nodes)):
            if color_dict[i] == 0:
                colors.append('red')
            if color_dict[i] == 1:
                colors.append('green')
            if color_dict[i] == 2:
                colors.append('blue')

    try:
        sanity_check_coloring(graph, colors)
        print('DSATUR: 3-coloring possible...')
    except InvalidColoringException:
        print('DSATUR: No 3-coloring possible!')
        return None

    return colors
