from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_generator import GraphGenerator

graph_generator = GraphGenerator(checker=GraphChecker)

configurations = [
    # [0.3, None, 3, True, None],
    # [0.5, None, 3, True, None],
    # [0.8, None, 3, True, None],
    # [0.3, 4, 5, None, None],
    # [0.5, 4, 5, None, None],
    # [0.8, 4, 5, None, None],
    # [0.3, 7, 3, None, None],
    # [0.5, 7, 3, None, None],
    [0.8, 7, 3, None, None],
]

for config in configurations:
    for n in [30]:
        g = graph_generator.find_graphs_with_conditions(n, config[0], config[1], config[2], config[3], config[4])
