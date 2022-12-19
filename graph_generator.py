import networkx as nx
import matplotlib.pyplot as plt

from graph_checker import GraphChecker


class GraphGenerator:

    def generate_graph(self, n, graph_type):
        return graph_type(n)


# graph_generator = GraphGenerator()
# graph = nx.generators.erdos_renyi_graph(10, 0.2, seed=0)
graph = nx.generators.erdos_renyi_graph(100, 0.20, seed=1287391)
nx.draw(graph, with_labels=True)
plt.show()

n = 7

contains_induced_path = GraphChecker().check_induced_path(graph, n)

print(contains_induced_path)
