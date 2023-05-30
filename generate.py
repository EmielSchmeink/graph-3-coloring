import time

from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_generator import GraphGenerator

graph_generator = GraphGenerator(checker=GraphChecker)

# p path cycle planar diameter locally_connected
configurations = [
    # [0.1, None, 3, True, None, None],
    [0.5, 7, 3, None, None, None],
    # [0.03, None, None, None, None, True],
]

for config in configurations:
    for n in [35000, 40000, 45000, 50000]:
        shuffle = True
        start_time = time.time()
        print(f"Generating graph with nodes {n}, p: {config[0]}, path: {config[1]}, cycle: {config[2]}, "
              f"planar: {config[3]}, diameter: {config[4]}, locally_connected: {config[5]}, shuffle: {shuffle}")
        g = graph_generator.find_graphs_with_conditions(n, config[0], config[1], config[2], config[3], config[4],
                                                        config[5], shuffle=shuffle)
        total_time = time.time() - start_time
        print(f"Generation took {total_time} seconds")
