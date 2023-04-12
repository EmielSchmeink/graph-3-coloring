class InvalidColoringException(Exception):
    """
    Exception indicating an invalid coloring.
    """
    pass


class InvalidGraphException(Exception):
    """
    Exception indicating an invalid graph.
    """
    pass


class InvalidMultigramException(Exception):
    """
    Exception indicating an invalid multigram.
    """
    pass


def sanity_check_coloring(graph, colors):
    """
    Check that the given color dict contains a color for all nodes.
    :param graph: The graph to be colored
    :param colors: The given coloring
    :raises InvalidColoringException
    """
    # Sanity check that all nodes have a color
    if len(colors) != len(graph.nodes):
        raise InvalidColoringException
