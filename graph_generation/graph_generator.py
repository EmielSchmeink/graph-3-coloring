import itertools
import os
import random
from datetime import datetime

import networkx as nx


class GraphGenerator:
    checker = None

    def __init__(self, checker):
        self.checker = checker()

    @staticmethod
    def write_graph(graph, p, path_length, cycle_size, planar, diameter):
        path = f"./graphs/graph-nodes-{graph.number_of_nodes()}-p-{p}-path-{path_length}-cycle-{cycle_size}-diameter-" \
               f"{diameter}-planar-{planar}-{datetime.now().strftime('%d-%m-%Y-%H:%M:%S')}.txt"
        if not os.path.exists("graphs/"):
            os.makedirs("graphs/")
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
                # print(f"Edge {e} was not okay")
                continue

            if cycle_size is not None and self.checker.check_induced_cycle(g, e[0], cycle_size):
                g.remove_edge(e[0], e[1])
                # print(f"Edge {e} was not okay")
                continue

            if path_length is not None and self.checker.check_induced_path(g, e, path_length):
                g.remove_edge(e[0], e[1])
                # print(f"Edge {e} was not okay")
                continue

            # print(f"Edge {e} was okay")

        # Sanity check graph
        from graph_generation.graph_drawer import draw_graph
        draw_graph(g, None)
        # self.checker.sanity_check_graph(g, path_length, cycle_size, planar, diameter)

        return g

    def find_graphs_with_conditions(self, queue, seed=0):
        # While there are tasks to do, keep running
        while not queue.empty():
            # Get the versions to compare
            nodes, p, path_length, cycle_size, planar, diameter = queue.get()

            print(
                f"Starting thread, amount of nodes: {nodes}, "
                f"p: {p}, path_length: {path_length}, "
                f"cycle_size: {cycle_size}, "
                f"planar: {planar}, "
                f"diameter {diameter}"
            )

            graph = self.erdos_renyi_with_checks(nodes, p, path_length, cycle_size, planar, diameter, seed=seed)

            # Graph passed all checks, save it
            self.write_graph(graph, p, path_length, cycle_size, planar, diameter)
