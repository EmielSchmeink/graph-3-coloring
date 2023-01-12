import networkx as nx
from networkx import NetworkXNoCycle
from networkx.algorithms.simple_paths import _empty_generator


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
    def is_path_cycle(graph, path):
        # For all paths check whether any node contains an edge to another node in the path, thus creating a cycle
        if len(path) == 2 or len(path) == 3:
            return False

        it = iter(path)

        for node in it:
            second_node = next(it, None)
            third_node = next(it, None)

            if second_node is None or third_node is None:
                return False

            path_without_neighbors = path.copy()
            path_without_neighbors.remove(node)
            path_without_neighbors.remove(second_node)
            path_without_neighbors.remove(third_node)

            for path_node in path_without_neighbors:
                if graph.has_edge(node, path_node) \
                        or graph.has_edge(second_node, path_node) \
                        or graph.has_edge(third_node, path_node):
                    return True

        return False

    @staticmethod
    def path_contains_new_edge(path, edge_node):
        if path[1] == edge_node:
            return True

        return False

    @staticmethod
    def check_induced_subpath(graph, path):
        # Check for each path if the simple path is an actual induced path
        induced_possible_path = nx.induced_subgraph(graph, path)
        induced_path_cycles = nx.cycle_basis(induced_possible_path)

        # The found path is an actual induced path, and does not contain cycles
        if len(induced_path_cycles) == 0:
            return True

        return False

    def add_found_path_to_edge_paths(self, found_path, path_length, edge_neighbor):
        # If the path contains the new edge, it must be the full path size, otherwise we don't care
        return self.path_contains_new_edge(found_path, edge_neighbor) and len(found_path) == path_length

    def all_simple_paths(self, graph, source, target, cutoff, edge_neighbor):
        if source not in graph:
            raise nx.NodeNotFound(f"source node {source} not in graph")
        if target in graph:
            targets = {target}
        else:
            try:
                targets = set(target)
            except TypeError as err:
                raise nx.NodeNotFound(f"target node {target} not in graph") from err
        if source in targets:
            return _empty_generator()
        if cutoff is None:
            cutoff = len(graph) - 1
        if cutoff < 1:
            return _empty_generator()

        # The dict of visited nodes
        visited = dict.fromkeys([source])
        stack = [iter(graph[source])]

        all_paths = []

        while stack:
            children = stack[-1]
            child = next(children, None)

            if child is None:
                stack.pop()
                visited.popitem()
            elif len(visited) < cutoff:
                if child in visited:
                    continue
                if child in targets:
                    found_path = list(visited) + [child]

                    # TODO huge speedup, but produces incorrect graphs
                    # if self.is_path_cycle(graph, found_path):
                    #     continue

                    all_paths.append(found_path)

                visited[child] = None

                if targets - set(visited.keys()):  # expand stack until find all targets
                    stack.append(iter(graph[child]))
                else:
                    visited.popitem()  # maybe other ways to child
            else:  # len(visited) == cutoff:
                for target in (targets & (set(children) | {child})) - set(visited.keys()):
                    found_path_cutoff = list(visited) + [target]

                    # if self.is_path_cycle(graph, found_path_cutoff):
                    #     continue

                    all_paths.append(found_path_cutoff)

                stack.pop()
                visited.popitem()

        return all_paths

    def check_induced_path(self, graph, edge, n):
        # Remove the source as a target
        vertices_without_sources = list(graph.nodes)
        vertices_without_sources.remove(edge[0])
        vertices_without_sources.remove(edge[1])

        graph_without_0 = graph.copy()
        graph_without_1 = graph.copy()

        graph_without_0.remove_node(edge[0])
        graph_without_1.remove_node(edge[1])

        # Separate the paths containing the new edge, and paths not containing the new edge
        paths_0 = self.all_simple_paths(graph_without_1, edge[0], vertices_without_sources, cutoff=n-1, edge_neighbor=edge[1])
        paths_1 = self.all_simple_paths(graph_without_0, edge[1], vertices_without_sources, cutoff=n-1, edge_neighbor=edge[0])

        # Make sure the edge nodes themselves also can be used to form a path
        paths_0.append([edge[0]])
        paths_1.append([edge[1]])

        # from graph_generation.graph_drawer import draw_graph
        # draw_graph(graph, None)

        # Loop over all combinations to form n sized paths from the left and right branch of the edge
        for length_path_0 in range(n):
            length_path_1 = n - length_path_0

            correct_length_path_0 = [path for path in paths_0 if len(path) == length_path_0]
            correct_length_path_1 = [path for path in paths_1 if len(path) == length_path_1]

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
