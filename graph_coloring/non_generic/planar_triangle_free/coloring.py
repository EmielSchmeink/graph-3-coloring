from graph_coloring.misc import intersection


def remove_neighbors_colors_from_allowed(neighbor, color_dict, allowed_colors):
    """
    Remove the color of the given neighbor from the given allowed colors list.
    :param neighbor: Node representing the neighbor
    :param color_dict: Dict containing fixed node: color pairs
    :param allowed_colors: List of allowed colors
    """
    neighbor_color = color_dict[neighbor]
    if neighbor_color in allowed_colors:
        allowed_colors.remove(neighbor_color)


def get_neighbors_coloring(neighbors, color_dict):
    """
    Remove already used colors by neighbors from the allowed colors.
    :param neighbors: Node representing the neighbor
    :param color_dict: Dict containing fixed node: color pairs
    :return: List with allowed colors
    """
    allowed_colors = ['red', 'green', 'blue']

    for neighbor in neighbors:
        if neighbor in color_dict:
            remove_neighbors_colors_from_allowed(neighbor, color_dict, allowed_colors)

    return allowed_colors


def get_identified_nodes(node):
    """
    If this node contains a '_', it is the identified node of all v1 v3 pairs of
    tetra and hexagrams it was involved in
    So split it and get the neighbors of those nodes as well to avoid conflicting colors
    If is a normal node it will just create a list of only that node
    :param node:
    :return:
    """
    return node.split('_')


def handle_node_coloring(node, graph, color_dict):
    """
    Color the given monogram, by checking its neighbors and greedily
    getting an allowed color, and update the color dict.
    :param node: Monogram to be colored
    :param graph: Graph to check neighbors in
    :param color_dict: Dict containing fixed node: color pairs
    """
    identified_nodes = get_identified_nodes(node)
    neighbors = []
    for identified_node in identified_nodes:
        neighbors.extend(graph.neighbors(identified_node))

    allowed_colors = get_neighbors_coloring(neighbors, color_dict)

    for identified_node in identified_nodes:
        color_dict[identified_node] = allowed_colors[0]


def handle_identified_node_coloring(multigram, color_dict):
    """
    Color the given tetra- or hexagram, and update the color dict.
    :param multigram: Tetra- or hexagram to be colored
    :param color_dict: Dict containing fixed node: color pairs
    """
    v_1 = multigram[0][0]
    v_3 = multigram[0][2]
    identified_nodes = get_identified_nodes(v_1)

    color_dict[v_3] = color_dict[identified_nodes[0]]


def get_allowed_colors(node, graph, color_dict):
    """
    Get the colors the given node can still be colored.
    :param node: Node to get allowed colors for
    :param graph: Graph to check the neighbors in
    :param color_dict: Dict containing the allowed colors of all nodes
    :return: List of colors that the given node can be colored
    """
    identified_nodes = get_identified_nodes(node)
    neighbors = graph.neighbors(identified_nodes[0])
    return get_neighbors_coloring(neighbors, color_dict)


def handle_v1_to_v4_coloring(multigram, graph, color_dict):
    """
    Color the given octagram or pentagram (all multigrams where v1 to v4 are reduced),
    and update the color dict.
    :param multigram: Octagram or pentagram to be colored
    :param graph: Graph to check neighbors in
    :param color_dict: Dict containing fixed node: color pairs
    """
    for i in range(2):
        # If the opposite nodes can use the same color, do so, because their neighbors might
        # not have any colors remaining otherwise
        node = multigram[0][i]
        opposite_node = multigram[0][i + 2 % 4]
        identified_node = get_identified_nodes(node)[0]
        identified_opposite_node = get_identified_nodes(opposite_node)[0]
        allowed_colors_node = get_allowed_colors(identified_node, graph, color_dict)
        allowed_colors_opposite_node = get_allowed_colors(identified_opposite_node, graph, color_dict)

        same_allowed_colors = intersection(allowed_colors_node, allowed_colors_opposite_node)

        if len(same_allowed_colors) == 0:
            color_dict[identified_node] = allowed_colors_node[0]
            color_dict[identified_opposite_node] = allowed_colors_opposite_node[0]
        else:
            color_dict[identified_node] = same_allowed_colors[0]
            color_dict[identified_opposite_node] = same_allowed_colors[0]


def handle_decagram_coloring(multigram, graph, color_dict):
    """
    Color decagram greedily.
    :param multigram: Decagram to color
    :param graph: Graph to get allowed colors in
    :param color_dict: Dict containing fixed node: color pairs
    """
    for node in multigram:
        allowed_colors = get_allowed_colors(node, graph, color_dict)
        identified_node = get_identified_nodes(node)[0]
        color_dict[identified_node] = allowed_colors[0]


def handle_multigram_coloring(multigram, graph, color_dict):
    """
    Color the graph using the given multigram.
    :param multigram: Multigram to be colored
    :param graph: Graph to check neighbors in
    :param color_dict: Dict containing fixed node: color pairs
    """
    match multigram[1]:
        case 'monogram':
            handle_node_coloring(multigram[0][0], graph, color_dict)
        case 'tetragram':
            handle_identified_node_coloring(multigram, color_dict)
        case 'octagram':
            handle_v1_to_v4_coloring(multigram, graph, color_dict)
        case 'pentagram':
            handle_v1_to_v4_coloring(multigram, graph, color_dict)
        case 'decagram':
            handle_decagram_coloring(multigram, graph, color_dict)
        case 'hexagram':
            handle_identified_node_coloring(multigram, color_dict)


def convert_multigrams_into_coloring(multigrams, graph):
    """
    Greedily color all multigrams, starting with the last added.
    :param multigrams: List of multigrams
    :param graph: Graph to check neighbors in
    :return: Dict of node: color pairs
    """
    color_dict = {}
    reverse_multigrams = multigrams.copy()
    reverse_multigrams.reverse()

    for multigram in reverse_multigrams:
        handle_multigram_coloring(multigram, graph, color_dict)

    return color_dict
