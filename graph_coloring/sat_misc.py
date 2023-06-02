from pysmt.shortcuts import Symbol, And, Not, Or, Solver
from tqdm import tqdm
from z3 import is_true


def create_model(graph):
    """
    Create a SAT formula in z3 representing the checking of the 3-coloring for the given graph.
    :param graph: Graph to be 3-colored
    :return: z3 model
    """
    edges = graph.edges()

    tqdm_nodes = tqdm(graph.nodes)
    tqdm_nodes.set_description(desc="Creating node clauses", refresh=True)

    s = Solver()

    for i in tqdm_nodes:
        r = Symbol(f"R_{i}")
        g = Symbol(f"G_{i}")
        b = Symbol(f"B_{i}")

        node_clause = And(
            Or(r, g, b),
            Or(Not(r), Not(g)),
            Or(Not(r), Not(b)),
            Or(Not(g), Not(b))
        )

        s.add_assertion(node_clause)

    tqdm_edges = tqdm(edges)
    tqdm_edges.set_description(desc="Creating edge clauses", refresh=True)

    for (i, j) in tqdm_edges:
        r_i = Symbol(f"R_{i}")
        g_i = Symbol(f"G_{i}")
        b_i = Symbol(f"B_{i}")

        r_j = Symbol(f"R_{j}")
        g_j = Symbol(f"G_{j}")
        b_j = Symbol(f"B_{j}")

        edge_clause = And(
            Or(Not(r_i), Not(r_j)),
            Or(Not(g_i), Not(g_j)),
            Or(Not(b_i), Not(b_j))
        )

        s.add_assertion(edge_clause)

    return s


def evaluate_model(model):
    """
    Get the color dict from the given z3 model where z3 has assigned each vertex a color.
    :param model: z3 model containing the coloring
    :return: Dict of colors for all vertices
    """
    colors_dict = {}
    tqdm_vertices = tqdm(model.z3_model.decls())
    tqdm_vertices.set_description(desc="Evaluating sat variables (3x the nodes)", refresh=True)

    for t in tqdm_vertices:
        if is_true(model.z3_model[t]):
            color, vertex = str(t).split('_')

            match color:
                case 'R':
                    colors_dict[vertex] = 'red'
                case 'G':
                    colors_dict[vertex] = 'green'
                case 'B':
                    colors_dict[vertex] = 'blue'

    return colors_dict
