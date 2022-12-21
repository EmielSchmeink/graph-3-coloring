import networkx as nx
from networkx import NetworkXNoCycle


class InvalidGraphException(Exception):
    pass


class GraphChecker:
    def sanity_check_graph(self, graph, path_length=None, cycle_size=None, planarity=None, diameter=None):
        if planarity is not None:
            planar = self.graph_check_planar(graph)
            print("Planar: {}".format(planar))

            if planar != planarity:
                raise InvalidGraphException("Graph wasn't correct planarity")

        if cycle_size is not None:
            contains_induced_cycle = self.graph_check_induced_cycle(graph, cycle_size)
            print("Contains induced cycle of length {}: {}".format(cycle_size, contains_induced_cycle))

            if contains_induced_cycle:
                raise InvalidGraphException("Graph had a cycle of size {}".format(cycle_size))

        if path_length is not None:
            contains_induced_path = self.graph_check_induced_path(graph, path_length)
            print("Contains induced path of length {}: {}".format(path_length, contains_induced_path))

            if contains_induced_path:
                raise InvalidGraphException("Graph had a path of size {}".format(path_length))

        if diameter is not None:
            diameter_smaller_or_equal = self.graph_check_diameter(graph, diameter)
            print("Graph diameter {} should be smaller than {}: {}".format(nx.diameter(graph), diameter, diameter_smaller_or_equal))

            # The diameter of the graph should be smaller or equal than the given diameter, so negate
            if not diameter_smaller_or_equal:
                raise InvalidGraphException(
                    "Graph had a diameter of size {}, while {} is required".format(nx.diameter(graph), diameter)
                )

    def graph_check_induced_path(self, graph, n):
        for node in graph:
            if self.check_induced_path(graph, node, n):
                return True

        return False

    @staticmethod
    def graph_check_induced_cycle(graph, c):
        if c == 3:
            # If any of the nodes contain a triangle, we got one
            for key, value in nx.triangles(graph).items():
                if value > 0:
                    return True
            return False

        cycles = nx.cycle_basis(graph)
        for cycle in cycles:
            if len(cycle) == c:
                return True

        return False

    @staticmethod
    def graph_check_planar(graph):
        return nx.is_planar(graph)

    @staticmethod
    def graph_check_diameter(graph, d):
        return nx.diameter(graph) <= d

    @staticmethod
    def check_induced_path(graph, node, n):
        # Remove the source as a target
        vertices_without_source = list(graph.nodes)
        vertices_without_source.remove(node)

        # Only get the paths with the size we care for
        correct_size_paths = [path for path in nx.all_simple_paths(graph, node, vertices_without_source, cutoff=n-1)
                              if len(path) == n]

        # Check for each path if the simple path is an actual induced path
        for path in correct_size_paths:
            induced_possible_path = nx.induced_subgraph(graph, path)
            induced_path_cycles = nx.cycle_basis(induced_possible_path)

            # The found path is an actual induced path, and does not contain cycles in
            if len(induced_path_cycles) == 0:
                return True

        return False

    @staticmethod
    def check_induced_cycle(graph, node, c):
        if c == 3:
            return nx.triangles(graph, node) > 0

        try:
            cycles = nx.find_cycle(graph, node)

            for cycle in cycles:
                if len(cycle) == c:
                    return True

            return False
        except NetworkXNoCycle:
            return False
