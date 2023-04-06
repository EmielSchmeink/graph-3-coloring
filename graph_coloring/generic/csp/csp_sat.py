from z3.z3 import *

from graph_coloring.sat_misc import evaluate_model


def vertex_color_list_sat(vertex, colors, R, G, B):
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

    for illegal_color in illegal_colors:
        if illegal_color == 'red':
            illegal_clause.append(Not(R(i)))
        if illegal_color == 'green':
            illegal_clause.append(Not(G(i)))
        if illegal_color == 'blue':
            illegal_clause.append(Not(B(i)))

    return And(
        Or(R(int(i)), G(int(i)), B(int(i))),
        Or(Not(R(int(i))), Not(G(int(i)))),
        Or(Not(R(int(i))), Not(B(int(i)))),
        Or(Not(G(int(i))), Not(B(int(i)))),
        And(illegal_clause)
    )


def create_vertex_sat(allowed_vertex_color_dict, R, G, B):
    """
    Create SAT clauses for all given vertices.
    :param allowed_vertex_color_dict: Dictionary containing the allowed colors for each vertex
    :param R: Function for Z3 representing the color red
    :param G: Function for Z3 representing the color green
    :param B: Function for Z3 representing the color blue
    :return: Z3 SAT clause
    """
    vertex_clauses = []

    for vertex, colors in allowed_vertex_color_dict.items():
        vertex_clauses.append(vertex_color_list_sat(vertex, colors, R, G, B))

    return And(vertex_clauses)


def create_edge_sat(graph, R, G, B):
    """
    Create SAT clauses for all edges s.t. the endpoints of the edges do not get the same color.
    :param graph: Graph with edges to be colored
    :param R: Function for Z3 representing the color red
    :param G: Function for Z3 representing the color green
    :param B: Function for Z3 representing the color blue
    :return: Z3 SAT clause
    """
    return And(
        [And(
            Or(Not(R(int(i))), Not(R(int(j)))),
            Or(Not(G(int(i))), Not(G(int(j)))),
            Or(Not(B(int(i))), Not(B(int(j))))
        ) for (i, j) in graph.edges]
    )


def csp_satisfier(graph, allowed_vertex_color_dict):
    """
    Create a coloring for the given graph with restrictions on what colors are allowed per vertex (list coloring).
    :param graph: Graph containing the vertices and edges
    :param allowed_vertex_color_dict: Dictionary containing the allowed colors for each vertex
    :return: Coloring of the given vertices
    """
    s = Solver()

    print('Making formula...')
    R = Function('R', IntSort(), BoolSort())
    G = Function('G', IntSort(), BoolSort())
    B = Function('B', IntSort(), BoolSort())

    vertex_sat = create_vertex_sat(allowed_vertex_color_dict, R, G, B)
    edge_sat = create_edge_sat(graph, R, G, B)
    s.add(And(vertex_sat, edge_sat))

    print('Solving...')
    is_sat = s.check()

    if is_sat == sat:
        print('CSP: Remaining SAT 3-coloring possible, evaluating model...')
    elif is_sat == unsat:
        print('CSP: No 3-coloring possible for this bushy tree coloring!')
        return None

    model = s.model()

    return evaluate_model(model, allowed_vertex_color_dict, R, G, B)
