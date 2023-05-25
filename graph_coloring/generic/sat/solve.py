import time

import pyprog
from z3.z3 import *

from graph_coloring.misc import write_results
from graph_coloring.sat_misc import evaluate_model


def sat_solve(graph, graph_name):
    """
    Get a 3-coloring for the given graph, or indicate that a 3-coloring is not possible, using a reduction to SAT, and
    solving using Z3.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes, or None
    """
    edges = graph.edges()
    s = Solver()

    print('SAT: Making formula...')
    start_time = time.time()

    R = Function('R', IntSort(), BoolSort())
    G = Function('G', IntSort(), BoolSort())
    B = Function('B', IntSort(), BoolSort())

    # Create a PyProg ProgressBar Object
    prog_node = pyprog.ProgressBar("Creating node clauses ", "OK!")
    node_clauses = []

    for i, node in enumerate(graph.nodes):
        # Update status
        prog_node.set_stat(i * 100 / len(graph.nodes))
        prog_node.update()

        node_clauses.append(And(
            Or(R(int(node)), G(int(node)), B(int(node))),
            Or(Not(R(int(node))), Not(G(int(node)))),
            Or(Not(R(int(node))), Not(B(int(node)))),
            Or(Not(G(int(node))), Not(B(int(node))))
        ))

    # Make the Progress Bar final
    prog_node.end()

    prog_edge = pyprog.ProgressBar("Creating edge clauses ", "OK!")
    edge_clauses = []

    for i, (e1, e2) in enumerate(edges):
        # Update status
        prog_edge.set_stat(i * 100 / len(edges))
        prog_edge.update()

        edge_clauses.append(And(
            Or(Not(R(int(e1))), Not(R(int(e2)))),
            Or(Not(G(int(e1))), Not(G(int(e2)))),
            Or(Not(B(int(e1))), Not(B(int(e2))))
        ))

    # Make the Progress Bar final
    prog_edge.end()

    s.add(And(
        And(node_clauses),
        And(edge_clauses)
    ))

    total_time = time.time() - start_time
    print(f"Formula creation took {total_time} seconds")

    write_results(graph_name, 'sat_formula', total_time)

    print('SAT: Solving...')
    is_sat = s.check()

    if is_sat == sat:
        print('SAT: 3-coloring possible, evaluating model...')
    elif is_sat == unsat:
        print('SAT: No 3-coloring possible!')
        return None

    model = s.model()
    return evaluate_model(model, graph.nodes, R, G, B)
