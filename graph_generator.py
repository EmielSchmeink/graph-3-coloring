import os
import random
import itertools
from datetime import datetime

import networkx as nx

from graph_checker import GraphChecker
from graph_printer import draw_graph
from sat import solve


class GraphGenerator:
    checker = None

    def __init__(self, checker):
        self.checker = checker()

    @staticmethod
    def write_graph(graph, p, path_length, cycle_size, planar, diameter):
        path = "./graphs/graph-nodes-{}-p-{}-path-{}-cycle-{}-diameter-{}-planar-{}-{}.txt".format(
            graph.number_of_nodes(),
            p,
            path_length,
            cycle_size,
            diameter,
            planar,
            datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
        )
        if not os.path.exists("./graphs/"):
            os.makedirs("./graphs/")
        nx.write_adjlist(graph, path)

    def erdos_renyi_with_checks(self, n, p, path_length=None, cycle_size=None, planar=None, diameter=None, seed=None):
        random.seed(seed)

        # All combinations of vertices that could become an edge
        edges = itertools.combinations(range(n), 2)
        g = nx.Graph()

        # Add all n vertices to the graph without edges
        g.add_nodes_from(range(n))

        for e in edges:
            # For each edge randomly make it a candidate
            if random.random() >= p:
                continue

            # If it is a candidate, add it to the graph and do the required checks
            g.add_edge(*e)

            # If the edge breaks a requirement, remove it and start with a new edge
            if planar is not None and planar != self.checker.graph_check_planar(g):
                g.remove_edge(e[0], e[1])
                continue

            if cycle_size is not None and self.checker.check_induced_cycle(g, e[0], cycle_size):
                g.remove_edge(e[0], e[1])
                continue

            if path_length is not None and self.checker.graph_check_induced_path(g, path_length):
                # TODO check why the individual induced path check doesn't work (sometimes produces induced paths)
                g.remove_edge(e[0], e[1])
                continue

            print("Edge {} was okay".format(e))

        # Sanity check graph
        self.checker.sanity_check_graph(g, path_length, cycle_size, planar, diameter)

        return g

    def find_graphs_with_conditions(self, nodes, p,
                                    path_length=None, cycle_size=None, planar=None, diameter=None, seed=0):
        print("Seed: {}".format(seed))
        graph = self.erdos_renyi_with_checks(nodes, p, path_length, cycle_size, planar, diameter, seed=seed)

        # Graph passed all checks, save it
        draw_graph(graph, None)

        # Save the graph to file
        self.write_graph(graph, p, path_length, cycle_size, planar, diameter)

        return graph


graph_generator = GraphGenerator(checker=GraphChecker)

configurations = [
    # [0.3, None, 3, True, None],
    # [0.5, None, 3, True, None],
    # [0.8, None, 3, True, None],
    [0.15, 4, 5, None, None],
    # [0.5, 4, 5, None, None],
    # [0.8, 4, 5, None, None],
    # [0.3, 7, 3, None, None],
    # [0.5, 7, 3, None, None],
    # [0.8, 7, 3, None, None],
]

for config in configurations:
    for n in [100]:
        g = graph_generator.find_graphs_with_conditions(n, config[0], config[1], config[2], config[3], config[4])

colors = solve(g.edges, len(g.nodes))
draw_graph(g, colors)
