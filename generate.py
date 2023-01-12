from multiprocessing import Process, Queue

from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_generator import GraphGenerator

graph_generator = GraphGenerator(checker=GraphChecker)

configurations = [
    [0.3, None, 3, True, None],
    [0.5, None, 3, True, None],
    [0.8, None, 3, True, None],
    [0.3, 4, 5, None, None],
    [0.5, 4, 5, None, None],
    [0.8, 4, 5, None, None],
    [0.3, 7, 3, None, None],
    [0.5, 7, 3, None, None],
    [0.8, 7, 3, None, None],
]

if __name__ == "__main__":
    # Create a queue for comparisons
    global_queue = Queue(maxsize=0)

    procs = []

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
