import networkx as nx

from graph_coloring.exceptions import sanity_check_coloring, InvalidColoringException


def dsatur_solve(graph):
    """
    Get a 3-coloring for the given graph, or indicate that a 3-coloring is not possible,
    using the DSATUR approximation algorithm.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes, or None
    """
    color_dict = nx.coloring.greedy_color(graph, strategy='DSATUR')

    for vertex, color in color_dict.items():
        match color:
            case 0:
                color_dict[vertex] = 'red'
            case 1:
                color_dict[vertex] = 'green'
            case 2:
                color_dict[vertex] = 'blue'
            case 3:
                # More than 3 colors were used, so invalid coloring
                print('DSATUR: No 3-coloring possible!')
                return None

    try:
        sanity_check_coloring(graph, color_dict)
        print('DSATUR: 3-coloring possible...')
    except InvalidColoringException:
        print('DSATUR: No 3-coloring possible!')
        return None

    return color_dict
