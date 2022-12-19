import networkx as nx
import matplotlib.pyplot as plt


class GraphChecker:
    @staticmethod
    def check_induced_path(graph, n):
        for node in graph:
            # Remove the source as a target
            vertices_without_source = list(graph.nodes)
            vertices_without_source.remove(node)

            correct_size_paths = [path for path in nx.all_simple_paths(graph, node, vertices_without_source, cutoff=n-1)
                                  if len(path) == n]

            # Check for each path if the simple path is an actual induced path
            for path in correct_size_paths:
                induced_possible_path = nx.induced_subgraph(graph, path)
                induced_path_cycles = nx.cycle_basis(induced_possible_path)

                # The found path is an actual induced path, and does not contain cycles in
                if len(induced_path_cycles) == 0:
                    return True
                # plt.clf()
                # nx.draw(induced_possible_path, with_labels=True)
                # plt.show()

        return False

    def check_induced_cycle(self, graph, n):
        pass

    def check_planar(self, graph):
        pass
