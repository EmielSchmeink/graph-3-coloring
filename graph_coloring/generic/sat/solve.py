import time

from tqdm import tqdm
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

    tqdm_nodes = tqdm(graph.nodes)
    tqdm_nodes.set_description(desc="Creating node clauses", refresh=True)

    node_clauses = [And(
        Or(R(int(i)), G(int(i)), B(int(i))),
        Or(Not(R(int(i))), Not(G(int(i)))),
        Or(Not(R(int(i))), Not(B(int(i)))),
        Or(Not(G(int(i))), Not(B(int(i))))
    ) for i in tqdm_nodes]

    tqdm_edges = tqdm(edges)
    tqdm_edges.set_description(desc="Creating edge clauses", refresh=True)
    edge_clauses = [And(
                Or(Not(R(int(i))), Not(R(int(j)))),
                Or(Not(G(int(i))), Not(G(int(j)))),
                Or(Not(B(int(i))), Not(B(int(j))))
            ) for (i, j) in tqdm_edges]

    s.add(And(
        And(node_clauses),
        And(edge_clauses)
    ))

    total_time = time.time() - start_time
    print(f"Formula creation took {total_time} seconds")

    write_results(graph_name, 'sat_formula', total_time)

    print('SAT: Solving...')
    start_time = time.time()

    is_sat = s.check()

    if is_sat == sat:
        print('SAT: 3-coloring possible, evaluating model...')
    elif is_sat == unsat:
        print('SAT: No 3-coloring possible!')
        return None

    total_time = time.time() - start_time
    print(f"Solving took {total_time} seconds")
    write_results(graph_name, 'sat_solving', total_time)

    model = s.model()
    return evaluate_model(model, graph.nodes, R, G, B)
