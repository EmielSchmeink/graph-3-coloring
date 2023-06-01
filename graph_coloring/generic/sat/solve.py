import time

from z3.z3 import *

from graph_coloring.misc import write_results
from graph_coloring.sat_misc import evaluate_model, create_model


def sat_solve(graph, graph_name):
    """
    Get a 3-coloring for the given graph, or indicate that a 3-coloring is not possible, using a reduction to SAT, and
    solving using Z3.
    :param graph: The graph to be colored
    :param graph_name: The path/name of the graph to be used to write results
    :return: Dict of colors for all nodes, or None
    """
    print('SAT: Making formula...')
    start_time = time.time()

    s = create_model(graph)

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
    return evaluate_model(model)
