import itertools
import logging
import os
import random
from datetime import datetime

import networkx as nx
import pyprog as pyprog

from graph_generation.graph_checker import GraphChecker


class GraphGenerator:
    checker: GraphChecker = None

    def __init__(self, checker):
        self.checker = checker()

    @staticmethod
    def write_graph(graph, path):
        path = f"./graphs/{path}.txt"
        if not os.path.exists("graphs/"):
            os.makedirs("graphs/")
        nx.write_adjlist(graph, path)

    def erdos_renyi_with_checks(self, n, p,
                                path_length=None, cycle_size=None, planar=None, diameter=None, shuffle=True, seed=None):
        random.seed(seed)

        # All combinations of vertices that could become an edge
        edges = list(itertools.combinations(range(n), 2))
        g = nx.Graph()

        if shuffle:
            random.shuffle(edges)

        # Add all n vertices to the graph without edges
        g.add_nodes_from(range(n))

        # Create a PyProg ProgressBar Object
        prog = pyprog.ProgressBar("Generation ", " OK!")

        for i, e in enumerate(edges):
            # Update status
            prog.set_stat(i * 100 / len(edges))
            prog.update()

            # For each edge randomly make it a candidate
            if random.random() >= p:
                continue

            # If it is a candidate, add it to the graph and do the required checks
            g.add_edge(*e)

            # If the edge breaks a requirement, remove it and start with a new edge
            if planar is not None and planar != self.checker.graph_check_planar(g):
                g.remove_edge(e[0], e[1])
                logging.info(f"Edge {e} was not okay")
                continue

            if cycle_size is not None and self.checker.check_induced_cycle(g, e, cycle_size):
                g.remove_edge(e[0], e[1])
                logging.info(f"Edge {e} was not okay")
                continue

            if path_length is not None and self.checker.check_induced_path(g, e, path_length):
                g.remove_edge(e[0], e[1])
                logging.info(f"Edge {e} was not okay")
                continue

            logging.info(f"Edge {e} was okay")

        # Make the Progress Bar final
        prog.end()

        # Sanity check graph
        from graph_generation.graph_drawer import draw_graph
        draw_graph(g, None)
        self.checker.sanity_check_graph(g, path_length, cycle_size, planar, diameter)

        return g

    def find_graphs_with_conditions(self, nodes, p,
                                    path_length=None, cycle_size=None, planar=None, diameter=None,
                                    shuffle=None, seed=0):
        print(f"Seed: {seed}")
        path = f"graph-nodes-{nodes}-p-{p}-path-{path_length}-cycle-{cycle_size}-diameter-" \
               f"{diameter}-planar-{planar}-shuffle-{shuffle}-{datetime.now().strftime('%d-%m-%Y-%H:%M:%S')}"

        if not os.path.exists("logs/"):
            os.makedirs("logs/")

        logging.basicConfig(filename=f"./logs/{path}.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

        graph = self.erdos_renyi_with_checks(nodes, p, path_length, cycle_size, planar, diameter, shuffle, seed)

        # Graph passed all checks, save it
        self.write_graph(graph, path)

        return graph
