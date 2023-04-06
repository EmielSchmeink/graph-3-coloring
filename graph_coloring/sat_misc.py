def evaluate_model(model, vertices, R, G, B):
    """
    Get the color dict from the given z3 model and for the given vertices, using the provided functions representing
    red, green, and blue respectively.
    :param model: z3 model containing the coloring
    :param vertices: The vertices to be colored
    :param R: Function representing red
    :param G: Function representing green
    :param B: Function representing blue
    :return: Dict of colors for all vertices
    """
    colors_dict = {}

    for vertex in vertices:
        i = int(vertex)
        is_red = model.evaluate(R(i))
        is_green = model.evaluate(G(i))
        is_blue = model.evaluate(B(i))

        if is_red:
            colors_dict[vertex] = 'red'
        if is_green:
            colors_dict[vertex] = 'green'
        if is_blue:
            colors_dict[vertex] = 'blue'

    return colors_dict
