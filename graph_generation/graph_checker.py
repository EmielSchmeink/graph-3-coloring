import networkx as nx
import planarity
from networkx import Graph
from tqdm import tqdm

from graph_coloring.exceptions import InvalidGraphException, InvalidColoringException


class GraphChecker:
    @staticmethod
    def valid_3_coloring(graph, coloring_dict):
        # Check that all vertices are colored, max 3 colors are used, and it is a valid coloring
        assert len(graph.nodes()) == len(coloring_dict)
        max_3 = len(set([colors for _, colors in coloring_dict.items()])) <= 3
        invalid_coloring = any([coloring_dict[x] == coloring_dict[y] for (x, y) in graph.edges()])

        if not max_3 or invalid_coloring:
            raise InvalidColoringException

    @staticmethod
    def get_color_offending_edge(graph, coloring_dict):
        tqdm_edges = tqdm(graph.edges())
        tqdm_edges.set_description(desc="Looping over edges", refresh=True)
        for (x, y) in tqdm_edges:
            if coloring_dict[x] == coloring_dict[y]:
                tqdm_edges.close()
                return x, y

    def sanity_check_graph(self, graph, path_length=None, cycle_size=None, planarity=None, diameter=None,
                           locally_connected=None, debug=None):
        if planarity is not None:
            planar = self.graph_check_planar(graph)
            print(f"Planar: {planar}")

            if planar != planarity:
                raise InvalidGraphException("Graph wasn't correct planarity")

        if cycle_size is not None:
            contains_induced_cycle = self.graph_check_induced_cycle(graph, cycle_size)
            if debug:
                print(f"Contains induced cycle of length {cycle_size}: {contains_induced_cycle}")

            if contains_induced_cycle:
                raise InvalidGraphException(f"Graph had a cycle of size {cycle_size}")

        if path_length is not None:
            contains_induced_path = self.graph_check_induced_path(graph, path_length, debug=debug)
            if debug:
                print(f"Contains induced path of length {path_length}: {contains_induced_path}")

            if contains_induced_path:
                raise InvalidGraphException(f"Graph had a path of size {path_length}")

        if diameter is not None:
            diameter_smaller_or_equal = self.graph_check_diameter(graph, diameter)
            print(f"Graph diameter {nx.diameter(graph)} should be smaller than {diameter}: {diameter_smaller_or_equal}")

            # The diameter of the graph should be smaller or equal than the given diameter, so negate
            if not diameter_smaller_or_equal:
                raise InvalidGraphException(
                    f"Graph had a diameter of size {nx.diameter(graph)}, while {diameter} is required"
                )

        if locally_connected is not None:
            graph_locally_connected = self.graph_check_locally_connected(graph)
            print(f"Graph should be locally connected, is: {graph_locally_connected}")

            # The diameter of the graph should be smaller or equal than the given diameter, so negate
            if not graph_locally_connected:
                raise InvalidGraphException(
                    f"Graph was not locally connected"
                )

    def graph_check_locally_connected(self, graph):
        for node in graph:
            print(f"Currently checking node {node} for locally connectedness")
            if not self.check_locally_connected(graph, [node]):
                return False

        return True

    def graph_check_induced_path(self, graph, n, debug=False):
        for node in graph:
            if debug:
                print(f"Currently checking node {node} for induced path")
            if self.get_induced_path(graph, [node], n):
                return True

        return False

    def graph_check_induced_cycle(self, graph, c):
        if c == 3:
            # If any of the nodes contain a triangle, we got one
            for key, value in nx.triangles(graph).items():
                if value > 0:
                    return True
            return False

        for edge in graph.edges:
            if len(self.check_induced_cycle_using_path(graph, edge, c)) > 0:
                return True

        return False

    @staticmethod
    def graph_check_planar(graph):
        return planarity.is_planar(graph)

    @staticmethod
    def graph_check_diameter(graph, d):
        return nx.diameter(graph) <= d

    @staticmethod
    def check_induced_path_brute_force(graph, node, n):
        # Remove the source as a target
        vertices_without_source = list(graph.nodes)
        vertices_without_source.remove(node)

        # Only get the paths with the size we care for
        correct_size_paths = [path for path in nx.all_simple_paths(graph, node, vertices_without_source, cutoff=n - 1)
                              if len(path) == n]

        # Check for each path if the simple path is an actual induced path
        for path in correct_size_paths:
            induced_possible_path = nx.induced_subgraph(graph, path)
            induced_path_cycles = nx.cycle_basis(induced_possible_path)

            # The found path is an actual induced path, and does not contain cycles in
            if len(induced_path_cycles) == 0:
                return True

    def get_induced_path(self, graph: Graph, s, length_remaining):
        if length_remaining <= 0:
            return s

        total_path = []
        last_path_node = s[-1]

        for v in graph.neighbors(last_path_node):
            # Check that the neighbor is not the previous node in the path
            if len(s) > 1 and v == s[-2]:
                continue

            # Check that no neighbors of v are in the path
            v_neighbor_in_path = False

            for v_neighbor in graph.neighbors(v):
                if not v_neighbor == last_path_node and v_neighbor in s:
                    v_neighbor_in_path = True
                    break

            if v_neighbor_in_path:
                continue

            # Add the neighbor as a possible induced path extension, but don't change s for the other extensions
            s_new = s.copy()
            s_new.append(v)
            total_path = self.get_induced_path(graph, s_new, length_remaining - 1)

            if len(total_path) > 0:
                return total_path

        return total_path

    def find_induced_path(self, graph: Graph, s, length_remaining, illegal_nodes):
        if length_remaining <= 0:
            return [s]

        last_path_node = s[-1]
        paths = []

        if last_path_node in illegal_nodes:
            return []

        for v in graph.neighbors(last_path_node):
            # Check that the neighbor is not the previous node in the path
            if len(s) > 1 and v == s[-2]:
                continue

            # Check that no neighbors of v are in the path
            v_neighbor_in_path = False

            for v_neighbor in graph.neighbors(v):
                if not v_neighbor == last_path_node and v_neighbor in s:
                    v_neighbor_in_path = True
                    break

            if v_neighbor_in_path:
                continue

            # Add the neighbor as a possible induced path extension, but don't change s for the other extensions
            s_new = s.copy()
            s_new.append(v)
            new_paths = self.find_induced_path(graph, s_new, length_remaining - 1, illegal_nodes)

            paths.extend(new_paths)

        # Add the current path as well
        paths.append(s)

        return paths

    def check_induced_path_using_edge(self, graph: Graph, edge, n):
        # Remove the source as a target
        graph_without_edge = graph.copy()
        graph_without_edge.remove_edge(edge[0], edge[1])

        # Separate the paths containing the new edge, and paths not containing the new edge
        paths_0 = self.find_induced_path(graph_without_edge, [edge[0]], n - 1, [edge[1], graph.neighbors(edge[1])])
        paths_1 = self.find_induced_path(graph_without_edge, [edge[1]], n - 1, [edge[0], graph.neighbors(edge[0])])

        # Loop over all combinations to form n sized paths from the left and right branch of the edge
        for length_path_0 in range(n):
            length_path_1 = n - length_path_0

            correct_length_path_0 = [path for path in paths_0 if len(path) == length_path_0]
            correct_length_path_1 = [path for path in paths_1 if len(path) == length_path_1]

            for path_0 in correct_length_path_0:
                for path_1 in correct_length_path_1:
                    if not self.check_crossing_edges(graph_without_edge, path_0, path_1):
                        return path_0 + path_1

        return []

    def check_induced_cycle_using_path(self, graph: Graph, edge, n):
        # Remove the source as a target
        graph_without_edge = graph
        graph_without_edge.remove_edge(edge[0], edge[1])

        # Separate the paths containing the new edge, and paths not containing the new edge
        print("Finding induced paths...")
        paths_0 = self.find_induced_path(graph_without_edge, [edge[0]], n - 1, [edge[1], graph.neighbors(edge[1])])
        paths_1 = self.find_induced_path(graph_without_edge, [edge[1]], n - 1, [edge[0], graph.neighbors(edge[0])])

        # Loop over all combinations to form n sized paths from the left and right branch of the edge
        tqdm_n = tqdm(range(n))
        tqdm_n.set_description(desc="Looping over path lengths", refresh=True)
        for length_path_0 in tqdm_n:
            length_path_1 = n - length_path_0

            correct_length_path_0 = [path for path in paths_0 if len(path) == length_path_0]
            correct_length_path_1 = [path for path in paths_1 if len(path) == length_path_1]

            for path_0 in correct_length_path_0:
                for path_1 in correct_length_path_1:
                    path_0_without_endpoint = path_0.copy()
                    path_1_without_endpoint = path_1.copy()
                    path_0_without_endpoint.pop(-1)
                    path_1_without_endpoint.pop(-1)
                    if not self.check_crossing_edges(graph, path_0, path_1_without_endpoint) or not \
                            self.check_crossing_edges(graph, path_0_without_endpoint, path_1):
                        endpoint_0 = path_0[-1]
                        endpoint_1 = path_1[-1]

                        if graph_without_edge.has_edge(endpoint_0, endpoint_1):
                            cycle = path_0.copy()
                            cycle.extend(path_1)
                            graph.add_edge(edge[0], edge[1])
                            return cycle

        graph.add_edge(edge[0], edge[1])
        return []

    def check_crossing_edges(self, graph: Graph, path_0, path_1):
        for v in path_0:
            for u in path_1:
                if graph.has_edge(v, u):
                    return True

        return False

    def check_induced_path(self, graph, edge, n):
        return len(self.check_induced_path_using_edge(graph, edge, n)) > 0

    def check_induced_cycle(self, graph, edge, c):
        if c == 3:
            return nx.triangles(graph, edge[0]) > 0

        return len(self.check_induced_cycle_using_path(graph, edge, c)) > 0

    def check_locally_connected(self, graph, nodes):
        for node in nodes:
            neighbors = list(graph.neighbors(node))
            induced_neighbors = nx.induced_subgraph(graph, neighbors)

            num_ccs = nx.number_connected_components(induced_neighbors)
            if num_ccs != 0 and num_ccs != 1:
                return False

        return True
