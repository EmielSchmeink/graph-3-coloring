from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_generator import GraphGenerator

from threading import Thread
from queue import Queue

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


# Create a queue for comparisons
global_queue = Queue(maxsize=0)

for config in configurations:
    for n in [10, 20, 50, 100]:
        global_queue.put([n, config[0], config[1], config[2], config[3], config[4]])

for num_threads in range(8):
    process = Thread(
        target=graph_generator.find_graphs_with_conditions,
        args=[global_queue]
    )
    process.daemon = True
    process.start()

# Join all threads to make sure that they have ended
global_queue.join()
print('We finished')
