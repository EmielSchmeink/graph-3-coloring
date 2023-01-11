import networkx as nx
from networkx import NetworkXNoCycle


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
        correct_size_paths = [path for path in nx.all_simple_paths(graph, node, vertices_without_source, cutoff=n-1)
                              if len(path) == n]

        # Check for each path if the simple path is an actual induced path
        for path in correct_size_paths:
            induced_possible_path = nx.induced_subgraph(graph, path)
            induced_path_cycles = nx.cycle_basis(induced_possible_path)

            # The found path is an actual induced path, and does not contain cycles in
            if len(induced_path_cycles) == 0:
                return True

    @staticmethod
    def get_paths_with_cycles(graph, paths):
        cycle_paths = []

        # For all paths check whether any node contains an edge to another node in the path, thus creating a cycle
        for path in paths:
            if len(path) == 2 or len(path) == 3:
                continue

            it = iter(path)

            for node in it:
                second_node = next(it, None)
                third_node = next(it, None)

                if second_node is None or third_node is None:
                    continue

                path_without_neighbors = path.copy()
                path_without_neighbors.remove(node)
                path_without_neighbors.remove(second_node)
                path_without_neighbors.remove(third_node)

                for path_node in path_without_neighbors:
                    if graph.has_edge(node, path_node) \
                            or graph.has_edge(second_node, path_node) \
                            or graph.has_edge(third_node, path_node):
                        cycle_paths.append(path)

        return cycle_paths

    @staticmethod
    def get_paths_with_new_edge(paths, edge_node):
        paths_with_new_edge = []

        for path in paths:
            if path[1] == edge_node:
                paths_with_new_edge.append(path)

        return paths_with_new_edge

    @staticmethod
    def check_induced_subpath(graph, path):
        # Check for each path if the simple path is an actual induced path
        induced_possible_path = nx.induced_subgraph(graph, path)
        induced_path_cycles = nx.cycle_basis(induced_possible_path)

        # The found path is an actual induced path, and does not contain cycles
        if len(induced_path_cycles) == 0:
            return True

        return False

    def check_induced_path(self, graph, edge, n):
        # Remove the source as a target
        vertices_without_source_0 = list(graph.nodes)
        vertices_without_source_1 = list(graph.nodes)
        vertices_without_source_0.remove(edge[0])
        vertices_without_source_1.remove(edge[1])

        all_paths_0 = [path for path in nx.all_simple_paths(graph, edge[0], vertices_without_source_0, cutoff=n - 1)]
        all_paths_1 = [path for path in nx.all_simple_paths(graph, edge[1], vertices_without_source_1, cutoff=n - 1)]

        # Separate the paths containing the new edge, and paths not containing the new edge
        filtered_paths_0_with_new_edge = self.get_paths_with_new_edge(all_paths_0, edge[1])
        filtered_paths_1_with_new_edge = self.get_paths_with_new_edge(all_paths_1, edge[0])

        for path in filtered_paths_0_with_new_edge:
            if len(path) == n and self.check_induced_subpath(graph, path):
                return True

        for path in filtered_paths_1_with_new_edge:
            if len(path) == n and self.check_induced_subpath(graph, path):
                return True

        # Get the paths with cycles
        cycle_paths_0 = self.get_paths_with_cycles(graph, all_paths_0)
        cycle_paths_1 = self.get_paths_with_cycles(graph, all_paths_1)

        all_paths_to_be_removed_0 = filtered_paths_0_with_new_edge
        all_paths_to_be_removed_1 = filtered_paths_1_with_new_edge

        for path in cycle_paths_0:
            if path not in all_paths_to_be_removed_0:
                all_paths_to_be_removed_0.append(path)

        for path in cycle_paths_1:
            if path not in all_paths_to_be_removed_1:
                all_paths_to_be_removed_1.append(path)

        filtered_paths_0 = all_paths_0.copy()
        filtered_paths_1 = all_paths_1.copy()

        for path in all_paths_to_be_removed_0:
            filtered_paths_0.remove(path)

        for path in all_paths_to_be_removed_1:
            filtered_paths_1.remove(path)

        # Loop over all combinations to form n sized paths from the left and right branch of the edge
        for length_path_0 in range(n):
            length_path_1 = n - length_path_0

            correct_length_path_0 = [path for path in filtered_paths_0 if len(path) == length_path_0]
            correct_length_path_1 = [path for path in filtered_paths_1 if len(path) == length_path_1]

            possible_induced_paths = []

            for path_0 in correct_length_path_0:
                for path_1 in correct_length_path_1:
                    concat_path = path_0 + path_1
                    possible_induced_paths.append(concat_path)

            for path in possible_induced_paths:
                if self.check_induced_subpath(graph, path):
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
