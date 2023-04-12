from graph_generation.graph_checker import GraphChecker
from multiprocessing import Process, Queue

from graph_generation.graph_generator import GraphGenerator

graph_generator = GraphGenerator(checker=GraphChecker)

# p path cycle planar diameter locally_connected
configurations = [
    [0.3, None, 3, True, None, None],
    [0.5, None, 3, True, None, None],
    [0.8, None, 3, True, None, None],
    [0.3, 4, 5, None, None, None],
    [0.5, 4, 5, None, None, None],
    [0.8, 4, 5, None, None, None],
    [0.3, 7, 3, None, None, None],
    [0.5, 7, 3, None, None, None],
    [0.5, 7, 3, None, None, None],
    [0.7, None, None, None, None, True],
]

if __name__ == "__main__":
    # Create a queue for comparisons
    global_queue = Queue(maxsize=0)

    procs = []

for config in configurations:
    for n in [100, 150, 200, 300]:
        shuffle = True
        print(f"Generating graph with nodes {n}, p: {config[0]}, path: {config[1]}, cycle: {config[2]}, "
              f"planar: {config[3]}, diameter: {config[4]}, locally_connected: {config[5]}, shuffle: {shuffle}")
        g = graph_generator.find_graphs_with_conditions(n, config[0], config[1], config[2], config[3], config[4],
                                                        config[5], shuffle=shuffle)
    for config in configurations:
        for n in [10, 20, 50, 100, 250, 500, 750, 1000]:
            global_queue.put([n, config[0], config[1], config[2], config[3], config[4]])

    for num_threads in range(10):
        proc = Process(target=graph_generator.find_graphs_with_conditions,
                       args=[global_queue])  # instantiating without any argument
        procs.append(proc)
        proc.start()

    # Join all threads to make sure that they have ended
    for proc in procs:
        proc.join()
    print('We finished')
