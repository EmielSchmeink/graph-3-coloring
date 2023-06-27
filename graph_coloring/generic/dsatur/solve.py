import itertools

from networkx.algorithms.coloring.greedy_coloring import strategy_saturation_largest_first
from tqdm import tqdm

from graph_coloring.exceptions import sanity_check_coloring, InvalidColoringException


def dsatur(graph):
    colors = {}
    nodes = strategy_saturation_largest_first(graph, colors)
    # nodes = strategy_largest_first(graph, colors)
    tqdm_nodes = tqdm(nodes, total=len(graph.nodes))
    tqdm_nodes.set_description(desc="Looping over nodes", refresh=True)

    for u in tqdm_nodes:
        # Set to keep track of colors of neighbours
        neighbour_colors = {colors[v] for v in graph[u] if v in colors}
        # Find the first unused color.
        for color in itertools.count():
            if color not in neighbour_colors:
                break
        # Assign the new color to the current node.
        colors[u] = color
    return colors


def dsatur_solve(graph):
    """
    Get a 3-coloring for the given graph, or indicate that a 3-coloring is not possible,
    using the DSATUR approximation algorithm.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes, or None
    """
    print('DSATUR: Creating coloring...')
    color_dict = dsatur(graph)

    print('DSATUR: Creating color dict...')
    color_set = set()
    for _, color in color_dict.items():
        color_set.add(color)

    if len(color_set) > 3:
        # More than 3 colors were used, so invalid coloring
        print(f'DSATUR: No 3-coloring possible! Used {len(color_set)} colors')

        return len(color_set)

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
                print('DSATUR: this is not supposed to happen')
                return None

    try:
        sanity_check_coloring(graph, color_dict)
        print('DSATUR: 3-coloring possible...')
    except InvalidColoringException:
        print('DSATUR: No 3-coloring possible!')
        return None

    return color_dict
