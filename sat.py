from z3 import *


def solve(edges, n):
    s = Solver()

    print('Making formula...')
    R = Function('R', IntSort(), BoolSort())
    G = Function('G', IntSort(), BoolSort())
    B = Function('B', IntSort(), BoolSort())

    s.add(And(
        And(
            [And(
                Or(R(i), G(i), B(i)),
                Or(Not(R(i)), Not(G(i))),
                Or(Not(R(i)), Not(B(i))),
                Or(Not(G(i)), Not(B(i)))
            ) for i in range(n)]
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
        print('3-coloring possible, evaluating model...')
    elif is_sat == unsat:
        print('No 3-coloring possible!')
        return None

    model = s.model()
    colors = []

    for i in range(n):
        is_red = model.evaluate(R(i))
        is_green = model.evaluate(G(i))
        is_blue = model.evaluate(B(i))

        if is_red:
            colors.append('red')
        if is_green:
            colors.append('green')
        if is_blue:
            colors.append('blue')

    print(s.model())
    return colors




