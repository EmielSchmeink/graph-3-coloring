from tqdm import tqdm
from z3.z3 import *


def create_model(graph):
    """
    Create a SAT formula in z3 representing the checking of the 3-coloring for the given graph.
    :param graph: Graph to be 3-colored
    :return: z3 model
    """
    edges = graph.edges()
    s = Solver()

    tqdm_nodes = tqdm(graph.nodes)
    tqdm_nodes.set_description(desc="Creating node clauses", refresh=True)

    for i in tqdm_nodes:
        r, g, b = Bools(f"R_{i} G_{i} B_{i}")

        node_clauses = [And(
            Or(r, g, b),
            Or(Not(r), Not(g)),
            Or(Not(r), Not(b)),
            Or(Not(g), Not(b))
        )]

        s.add(node_clauses)

    tqdm_edges = tqdm(edges)
    tqdm_edges.set_description(desc="Creating edge clauses", refresh=True)

    for (i, j) in tqdm_edges:
        r_i, g_i, b_i = Bools(f"R_{i} G_{i} B_{i}")
        r_j, g_j, b_j = Bools(f"R_{j} G_{j} B_{j}")

        edge_clauses = [And(
            Or(Not(r_i), Not(r_j)),
            Or(Not(g_i), Not(g_j)),
            Or(Not(b_i), Not(b_j))
        )]

        s.add(edge_clauses)

    return s


def evaluate_model(model):
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

    tqdm_vertices = tqdm(model.decls())
    tqdm_vertices.set_description(desc="Evaluating vertices", refresh=True)

    for t in tqdm_vertices:
        if is_true(model[t]):
            color, vertex = str(t).split('_')

            match color:
                case 'R':
                    colors_dict[vertex] = 'red'
                case 'G':
                    colors_dict[vertex] = 'green'
                case 'B':
                    colors_dict[vertex] = 'blue'

    return colors_dict
