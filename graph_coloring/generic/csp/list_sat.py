from z3.z3 import *

from graph_coloring.sat_misc import evaluate_model, create_model


def illegal_color_clauses(vertex, colors):
    """
    Create SAT clauses so that it only is colors one and only one color for the given vertex,
    with given colors as options.
    :param vertex: The vertex to create a SAT clause for
    :param colors: List of colors which the vertex can be colored
    :param R: Function for Z3 representing the color red
    :param G: Function for Z3 representing the color green
    :param B: Function for Z3 representing the color blue
    :return: Z3 SAT clause
    """
    i = int(vertex)

    illegal_colors = [color for color in ['red', 'green', 'blue'] if color not in colors]
    illegal_clause = []

    r, g, b = Bools(f"R_{i} G_{i} B_{i}")

    for illegal_color in illegal_colors:
        if illegal_color == 'red':
            illegal_clause.append(Not(r))
        if illegal_color == 'green':
            illegal_clause.append(Not(g))
        if illegal_color == 'blue':
            illegal_clause.append(Not(b))

    return And(illegal_clause)


def list_sat_satisfier(graph, allowed_vertex_color_dict):
    """
    Create a coloring for the given graph with restrictions on what colors are allowed per vertex (list coloring).
    :param graph: Graph containing the vertices and edges
    :param allowed_vertex_color_dict: Dictionary containing the allowed colors for each vertex
    :return: Coloring of the given vertices
    """
    s = create_model(graph)

    for vertex, colors in allowed_vertex_color_dict.items():
        clause = illegal_color_clauses(vertex, colors)
        s.add(clause)

    print('List SAT: Solving...')
    is_sat = s.check()

    if is_sat == sat:
        print('List SAT: Remaining SAT 3-coloring possible, evaluating model...')
    elif is_sat == unsat:
        print('List SAT: No 3-coloring possible for this bushy tree coloring!')
        return None

    model = s.model()

    return evaluate_model(model)
