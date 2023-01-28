import networkx as nx
from networkx import NetworkXNoCycle, Graph


class InvalidGraphException(Exception):
    pass


class GraphChecker:
    @staticmethod
    def valid_3_coloring(graph, coloring):
        # Check that max 3 colors are used, and it is a valid coloring
        max_3 = len(set(coloring)) <= 3
        invalid_coloring = any([coloring[int(x)] == coloring[int(y)] for (x, y) in graph.edges()])
        return max_3 and not invalid_coloring

    def sanity_check_graph(self, graph, path_length=None, cycle_size=None, planarity=None, diameter=None):
        if planarity is not None:
            planar = self.graph_check_planar(graph)
            print(f"Planar: {planar}")

            if planar != planarity:
                raise InvalidGraphException("Graph wasn't correct planarity")

        if cycle_size is not None:
            contains_induced_cycle = self.graph_check_induced_cycle(graph, cycle_size)
            print(f"Contains induced cycle of length {cycle_size}: {contains_induced_cycle}")

            if contains_induced_cycle:
                raise InvalidGraphException(f"Graph had a cycle of size {cycle_size}")

        if path_length is not None:
            contains_induced_path = self.graph_check_induced_path(graph, path_length)
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

    def graph_check_induced_path(self, graph, n):
        for node in graph:
            print(f"Currently checking node {node}")
            if self.check_induced_path_old(graph, node, n):
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
    def check_induced_path_old(graph, node, n):
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

    def find_induced_path(self, graph: Graph, s, length_remaining, illegal_nodes):
        if length_remaining <= 0:
            return [s]

        last_path_node = s[-1]
        paths = []

        for v in graph.neighbors(last_path_node):
            # Check that the neighbor is not the previous node in the path
            if len(s) > 1 and v == s[-2]:
                continue

            if v in illegal_nodes:
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

    def check_induced_path(self, graph: Graph, edge, n):
        # Remove the source as a target
        graph_without_edge = graph.copy()
        graph_without_edge.remove_edge(edge[0], edge[1])

        # Separate the paths containing the new edge, and paths not containing the new edge
        paths_0 = self.find_induced_path(graph_without_edge, [edge[0]], n - 1, [])
        paths_1 = self.find_induced_path(graph_without_edge, [edge[1]], n - 1, [])

        flat_list_0 = set([item for sublist in paths_0 for item in sublist])
        flat_list_1 = set([item for sublist in paths_1 for item in sublist])

        correct_paths_0 = self.find_induced_path(graph_without_edge, [edge[0]], n - 1, flat_list_0)
        correct_paths_1 = self.find_induced_path(graph_without_edge, [edge[1]], n - 1, flat_list_1)

        # Loop over all combinations to form n sized paths from the left and right branch of the edge
        for length_path_0 in range(n):
            length_path_1 = n - length_path_0

            correct_length_path_0 = [path for path in correct_paths_0 if len(path) == length_path_0]
            correct_length_path_1 = [path for path in correct_paths_1 if len(path) == length_path_1]

            for path_0 in correct_length_path_0:
                for path_1 in correct_length_path_1:
                    if not self.check_crossing_edges(graph_without_edge, path_0, path_1):
                        return True

        return False

    def check_crossing_edges(self, graph: Graph, path_0, path_1):
        for v in path_0:
            for u in path_1:
                if graph.has_edge(v, u):
                    return True

        return False

    @staticmethod
    def check_induced_cycle(graph, node, c):
        if c == 3:
            return nx.triangles(graph, node) > 0

        try:
            cycles = nx.cycle_basis(graph, node)

            for cycle in cycles:
                if len(cycle) == c:
                    return True

            return False
        except NetworkXNoCycle:
            return False
