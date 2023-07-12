import itertools
import logging
import os
import random
from datetime import datetime

import networkx as nx
from tqdm import tqdm

from graph_coloring.misc import intersection
from graph_generation.graph_checker import GraphChecker
from graph_generation.graph_drawer import draw_graph


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

    def split_list(self, alist, wanted_parts=1):
        length = len(alist)
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
                for i in range(wanted_parts)]

    def erdos_renyi_with_checks(self, n, p,
                                path_length=None, cycle_size=None, planar=None, diameter=None, locally_connected=None,
                                shuffle=True, seed=None, batch_size=1):
        random.seed(seed)

        # All combinations of vertices that could become an edge
        edges = list(itertools.combinations(range(n), 2))
        g = nx.Graph()

        if shuffle:
            random.shuffle(edges)

        # Add all n vertices to the graph without edges
        g.add_nodes_from(range(n))

        tqdm_edges = tqdm(edges)
        tqdm_edges.set_description(desc="Checking edges")

        batch_edges = []

        for e in tqdm_edges:
            # For each edge randomly make it a candidate
            if random.random() >= p:
                continue

            batch_edges.append(e)

            # If it is a candidate, add it to the graph and do the required checks
            g.add_edge(*e)

            if len(batch_edges) % batch_size != 0:
                continue

            # If the edge breaks a requirement, remove it and start with a new edge
            if planar is not None and planar != self.checker.graph_check_planar(g):
                for edge in batch_edges:
                    g.remove_edge(edge[0], edge[1])

                logging.info(f"Edge {e} was not okay")
                batch_edges = []
                continue

            if cycle_size is not None:
                for edge in batch_edges:
                    if self.checker.check_induced_cycle(g, edge, cycle_size):
                        g.remove_edge(edge[0], edge[1])

                logging.info(f"Edge {e} was not okay")
                batch_edges = []
                continue

            if path_length is not None and self.checker.check_induced_path(g, e, path_length):
                g.remove_edge(e[0], e[1])
                logging.info(f"Edge {e} was not okay")
                continue

            batch_edges = []
            logging.info(f"Edge {e} was okay")

        if planar is not None and planar != self.checker.graph_check_planar(g):
            for edge in batch_edges:
                g.remove_edge(edge[0], edge[1])

            logging.info(f"Edge {e} was not okay")

        if cycle_size is not None and self.checker.check_induced_cycle(g, e, cycle_size):
            for edge in batch_edges:
                g.remove_edge(edge[0], edge[1])

            logging.info(f"Edge {e} was not okay")

        # Sanity check graph
        draw_graph(g, None)
        self.checker.sanity_check_graph(g, path_length, cycle_size, planar, diameter, locally_connected)

        return g

    def make_neighbors_connected(self, graph, node):
        neighbors = list(graph.neighbors(node))
        induced_neighbors = nx.induced_subgraph(graph, neighbors)

        ccs = list(nx.connected_components(induced_neighbors))

        for i in range(len(ccs) - 1):
            cc_1 = list(ccs[i])
            cc_2 = list(ccs[i + 1])

            graph.add_edge(cc_1[0], cc_2[0])

    def locally_connected_generation(self, n, p, seed=None):
        random.seed(seed)

        print('Generating erdos renyi graph')
        graph = nx.gnp_random_graph(n, p, seed)
        print('Done generating erdos renyi graph')

        tqdm_nodes = tqdm(list(graph.nodes))
        tqdm_nodes.set_description(desc="Checking nodes")

        for node in tqdm_nodes:
            is_locally_connected = self.checker.check_locally_connected(graph, [node])
            if not is_locally_connected:
                self.make_neighbors_connected(graph, node)

        ccs = list(nx.connected_components(graph))
        tqdm_ccs = tqdm(range(len(ccs) - 1))
        tqdm_ccs.set_description(desc="Checking ccs")

        for i in tqdm_ccs:
            cc1 = list(ccs[i])
            cc2 = list(ccs[i+1])

            node1 = cc1[0]
            node2 = cc2[0]

            graph.add_edge(node1, node2)

            self.make_neighbors_connected(graph, node1)
            self.make_neighbors_connected(graph, node2)

        draw_graph(graph, None)
        self.checker.sanity_check_graph(graph, locally_connected=True)

        return graph

    def connect_components(self, graph, cc1, cc2, path_length):
        for node1 in cc1:
            for node2 in cc2:
                disconnected_graph = graph.copy()
                disconnected_graph.add_edge(node1, node2)

                if not self.checker.check_induced_path(disconnected_graph, (node1, node2), path_length):
                    graph.add_edge(node1, node2)
                    return

        print('Components could not be connected...')
        return

    def try_make_induced_path_free_graph_connected(self, graph, path_length, cycle_size, planar, diameter,
                                                   locally_connected):
        to_be_connected_graph = graph.copy()
        ccs = list(nx.connected_components(to_be_connected_graph))

        if len(ccs) == 1:
            print('Graph was already connected...')
            return to_be_connected_graph

        for cc1 in ccs:
            for cc2 in ccs:
                if cc1 == cc2:
                    break

                self.connect_components(to_be_connected_graph, cc1, cc2, path_length)

                if len(list(nx.connected_components(to_be_connected_graph))) == 1:
                    self.checker.sanity_check_graph(graph, path_length, cycle_size, planar, diameter, locally_connected)
                    return to_be_connected_graph

        self.checker.sanity_check_graph(graph, path_length, cycle_size, planar, diameter, locally_connected)
        return to_be_connected_graph

    def fix_induced_path(self, graph, path):
        reverse_path = path.copy()
        reverse_path.reverse()

        for i, node1 in enumerate(path):
            for j, node2 in enumerate(reverse_path):
                neighbors1 = list(graph.neighbors(node1))
                neighbors2 = list(graph.neighbors(node2))
                overlap = intersection(neighbors1, neighbors2)

                node1_has_node2_neighbor = intersection(neighbors1, [node2])
                node2_has_node1_neighbor = intersection(neighbors2, [node1])

                if len(node1_has_node2_neighbor) == 0 and len(node2_has_node1_neighbor) == 0 and len(overlap) == 0:
                    graph.add_edge(node1, node2)
                    return True

        # Could not fix path, greedily removing edge in the path
        # for i in range(len(path)-1):
        #     if graph.has_edge(path[i], path[i+1]):
        #         graph.remove_edge(path[i], path[i+1])
        return False

    def fully_connect_sets(self, graph, set1, set2):
        edges = []

        for node1 in set1:
            for node2 in set2:
                edges.append((node1, node2))

        graph.add_edges_from(edges)

    def path_free_generation(self, nodes, p, path_length, cycle_size, shuffle, seed=123):
        random.seed(seed)

        graph = nx.Graph()
        graph.add_nodes_from(range(nodes))

        print("Starting connecting sets...")
        node_partitions = self.split_list(list(graph.nodes), 6)

        print("Connecting sets 0 and 1...")
        self.fully_connect_sets(graph, node_partitions[0], node_partitions[1])

        print("Connecting sets 1 and 2...")
        self.fully_connect_sets(graph, node_partitions[1], node_partitions[2])

        print("Connecting sets 3 and 4...")
        self.fully_connect_sets(graph, node_partitions[3], node_partitions[4])

        print("Connecting sets 4 and 5...")
        self.fully_connect_sets(graph, node_partitions[4], node_partitions[5])

        node0 = node_partitions[0][-1]
        node2 = node_partitions[2][-1]
        node3 = node_partitions[3][0]
        node4 = node_partitions[4][0]

        graph.add_edge(node0, node3)
        graph.add_edge(node2, node4)

        draw_graph(graph, None)
        assert len(list(nx.connected_components(graph))) == 1
        # self.checker.sanity_check_graph(graph, path_length=path_length, cycle_size=cycle_size, debug=True)
        print(nx.density(graph))

        return graph

    def find_graphs_with_conditions(self, nodes, p,
                                    path_length=None, cycle_size=None, planar=None, diameter=None,
                                    locally_connected=None, shuffle=None, seed=0):
        print(f"Seed: {seed}")
        path = f"graph-nodes-{nodes}-p-{p}-path-{path_length}-cycle-{cycle_size}-" \
               f"planar-{planar}-diameter-{diameter}-locally_connected-{locally_connected}-shuffle-{shuffle}" \
               f"-{datetime.now().strftime('%d-%m-%Y-%H:%M:%S')}"

        if not os.path.exists("logs/"):
            os.makedirs("logs/")

        logging.basicConfig(filename=f"./logs/{path}.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

        if locally_connected is not None:
            graph = self.locally_connected_generation(nodes, p, seed)
        elif path_length is not None:
            graph = self.path_free_generation(nodes, p, path_length, cycle_size, shuffle, seed)
        else:
            graph = self.erdos_renyi_with_checks(nodes, p, path_length, cycle_size, planar, diameter,
                                                 locally_connected, shuffle, seed)
            # graph = self.embedding_generation(nodes, p, seed)

        # Graph passed all checks, save it
        self.write_graph(graph, path)

        return graph, path
