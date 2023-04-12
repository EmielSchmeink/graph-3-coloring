from z3.z3 import *

from graph_coloring.sat_misc import evaluate_model


def sat_solve(graph):
    """
    Get a 3-coloring for the given graph, or indicate that a 3-coloring is not possible, using a reduction to SAT, and
    solving using Z3.
    :param graph: The graph to be colored
    :return: Dict of colors for all nodes, or None
    """
    edges = graph.edges()
    s = Solver()

    print('Making formula...')
    R = Function('R', IntSort(), BoolSort())
    G = Function('G', IntSort(), BoolSort())
    B = Function('B', IntSort(), BoolSort())

    s.add(And(
        And(
            [And(
                Or(R(int(i)), G(int(i)), B(int(i))),
                Or(Not(R(int(i))), Not(G(int(i)))),
                Or(Not(R(int(i))), Not(B(int(i)))),
                Or(Not(G(int(i))), Not(B(int(i))))
            ) for i in graph.nodes]
        ),
        And(
            [And(
                Or(Not(R(int(i))), Not(R(int(j)))),
                Or(Not(G(int(i))), Not(G(int(j)))),
                Or(Not(B(int(i))), Not(B(int(j))))
            ) for (i, j) in edges]
        )
    ))

    print('Solving...')
    is_sat = s.check()

    if is_sat == sat:
        print('SAT: 3-coloring possible, evaluating model...')
    elif is_sat == unsat:
        print('SAT: No 3-coloring possible!')
        return None

    model = s.model()
    return evaluate_model(model, graph.nodes, R, G, B)
