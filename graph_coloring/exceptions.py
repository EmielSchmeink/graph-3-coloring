class InvalidColoringException(Exception):
    pass


def sanity_check_coloring(graph, colors):
    # Sanity check that all nodes have a color
    if len(colors) != len(graph.nodes):
        raise InvalidColoringException
