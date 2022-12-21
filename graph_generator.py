import os
import random
import itertools
from datetime import datetime

import networkx as nx

from graph_checker import GraphChecker
from graph_printer import draw_graph

checker = GraphChecker()


def write_graph(graph, p, path_length, cycle_size, planarity):
    path = "./graphs/graph-nodes-{}-p-{}-path-{}-cycle-{}-planar-{}-{}.txt".format(
        graph.number_of_nodes(),
        p,
        path_length,
        cycle_size,
        planarity,
        datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
    )
    if not os.path.exists("./graphs/"):
        os.makedirs("./graphs/")
    nx.write_adjlist(graph, path)


def erdos_renyi_with_checks(n, p, path_length=None, cycle_size=None, planarity=None, seed=None):
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
        if planarity is not None:
            planar = checker.graph_check_planar(g)

            if planar != planarity:
                g.remove_edge(e[0], e[1])
                continue

        if cycle_size is not None:
            contains_induced_cycle = checker.check_induced_cycle(g, e[0], cycle_size)

            if contains_induced_cycle:
                g.remove_edge(e[0], e[1])
                continue

        if path_length is not None:
            # TODO check why the individual induced path check doesn't work (sometimes produces induced paths)
            contains_induced_path = checker.graph_check_induced_path(g, path_length)

            if contains_induced_path:
                g.remove_edge(e[0], e[1])
                continue

        print("Edge {} was okay".format(e))

    # Sanity check graph
    checker.sanity_check_graph(g, path_length, cycle_size, planarity)

    return g


def find_graphs_with_conditions(nodes, p, graphs_to_be_found, path_length=None, cycle_size=None, planarity=None):
    seed = -1

    # If we need multiple graphs, we continue until the required amount is found
    while graphs_to_be_found > 0:
        seed += 1
        print("Seed: {}".format(seed))

        graph = erdos_renyi_with_checks(nodes, p, path_length, cycle_size, planarity, seed=seed)

        # Graph passed all checks, save it
        draw_graph(graph)

        # Save the graph to file
        write_graph(graph, p, path_length, cycle_size, planarity)

        graphs_to_be_found -= 1


find_graphs_with_conditions(nodes=50, p=0.5, graphs_to_be_found=1, path_length=7, cycle_size=3, planarity=None)
