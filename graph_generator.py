import random
import time
from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx

from graph_checker import GraphChecker


def triangle_free_graph(total_nodes):
    """Construct a triangle free graph."""
    nodes = range(total_nodes)
    g = nx.Graph()
    g.add_nodes_from(nodes)
    edge_candidates = list(combinations(nodes, 2))
    random.shuffle(edge_candidates)
    for (u, v) in edge_candidates:
        if not set(n for n in g.neighbors(u)) & set(n for n in g.neighbors(v)):
            g.add_edge(u, v)
    return g


def find_graphs_with_conditions(nodes, graphs_to_be_found, path_length=None, cycle_size=None, planarity=None):
    seed = -1

    while graphs_to_be_found > 0:
        seed += 1
        print("Seed: {}".format(seed))

        # graph = nx.generators.erdos_renyi_graph(15, 0.2, seed=seed)
        graph = triangle_free_graph(nodes)

        if planarity is not None:
            planar = GraphChecker().check_planar(graph)
            print("Planar: {}".format(planar))

            if planar != planarity:
                continue

        if cycle_size is not None:
            contains_induced_cycle = GraphChecker().check_induced_cycle(graph, cycle_size)
            print("Contains induced cycle of length {}: {}".format(cycle_size, contains_induced_cycle))

            if contains_induced_cycle:
                continue

        if path_length is not None:
            contains_induced_path = GraphChecker().check_induced_path(graph, path_length)
            print("Contains induced path of length {}: {}".format(path_length, contains_induced_path))

            if contains_induced_path:
                continue

        # Graph passed all checks, save it
        nx.draw(graph, with_labels=True)
        plt.show()
        nx.write_adjlist(graph, "./graphs/graph-{}.txt".format(time.time()))

        graphs_to_be_found -= 1


find_graphs_with_conditions(nodes=15, graphs_to_be_found=1, path_length=None, cycle_size=3, planarity=True)
