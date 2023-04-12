import itertools

import networkx as nx

from graph_coloring.misc import get_vertices_of_degree_n, intersection


class K13:
    """Class representing a K1,3 instance."""
    center: str
    neighbors: list
    neighbors_edges: list
    tree_grandchildren: list

    def __init__(self, center, neighbors, graph):
        self.center = center
        self.neighbors = neighbors
        self.neighbors_edges = []
        self.tree_grandchildren = []

        for neighbor in neighbors:
            self.neighbors_edges.extend(
                [edge for edge in graph.edges([neighbor]) if edge[0] != center and edge[1] != center])

    def check_if_k13_exists(self, graph: nx.Graph):
        """
        Check if this K13 exists in the given graph.
        :param graph: Graph to check if it contains this K13
        :return: True if given graph contains this K13, False else
        """
        if len(self.neighbors) != 3:
            raise Exception('A K1,3 must contain exactly 3 neighbors.')

        return graph.has_node(self.center) \
            and graph.has_node(self.neighbors[0]) \
            and graph.has_node(self.neighbors[1]) \
            and graph.has_node(self.neighbors[2])

    def get_k13_edges(self):
        """
        Get all internal edges of this K13.
        :return: List of edges
        """
        return [(self.center, neighbor) for neighbor in self.neighbors]

    def remove_k13_from_graph(self, graph: nx.Graph):
        """
        Remove K13 from the given graph.
        :param graph: Graph to be removed from
        """
        graph.remove_node(self.center)
        graph.remove_nodes_from(self.neighbors)

    def add_k13_to_graph(self, graph: nx.Graph):
        """
        Add K13 to the given graph.
        :param graph: Graph to be added to
        """
        graph.add_node(self.center)
        graph.add_nodes_from(self.neighbors)
        graph.add_edges_from(self.get_k13_edges())
        graph.add_edges_from(self.neighbors_edges)

    def get_k13_grandchildren(self):
        """
        Get the grandchildren of this K13.
        :return: List of unique grandchildren
        """
        neighbor_vertices = []

        for neighbor_edge in self.neighbors_edges:
            if neighbor_edge[0] in self.neighbors:
                neighbor_vertices.append(neighbor_edge[1])
            else:
                neighbor_vertices.append(neighbor_edge[0])

        return list(set(neighbor_vertices))

    def get_children_dict(self):
        """
        Get the dict of all children of the K13 (so only center).
        :return: Dict of children
        """
        return {self.center: self.neighbors}


def get_maximal_set_of_k13(graph):
    """
    Get a maximal K13 list for a given graph, by getting all degree 3 nodes and extending it using the rules of the
    K13, until all degree 3 nodes have been checked if they are part of a K13.
    :param graph: Graph in which the K13 must be created
    :return: List of K13
    """
    graph_without_maximal_k13 = graph.copy()

    degree_3 = get_vertices_of_degree_n(graph_without_maximal_k13, 3)

    k13_list = []

    for vertex in degree_3:
        # If the vertex was already removed by another K1,3 we skip it
        if graph_without_maximal_k13.has_node(vertex):
            neighbors = [v for v in nx.neighbors(graph_without_maximal_k13, vertex)]
        else:
            continue

        # If one of the neighbors was already removed, we skip the center vertex
        if len(neighbors) != 3:
            continue

        possible_k13 = K13(vertex, neighbors, graph)

        # Save this K1,3 and remove it from the graph
        k13_list.append(possible_k13)
        possible_k13.remove_k13_from_graph(graph_without_maximal_k13)

    return k13_list


def optimize_k13_list(graph, k13_list):
    """
    Check if we can create 2 more K13s by removing 1 and choosing different centers.
    :param graph: Graph containing the K13s
    :param k13_list: The original list of K13s
    :return: An optimized list of K13s
    """
    todo_k13_list = k13_list.copy()
    optimized_k13_list = []

    while len(todo_k13_list) > 0:
        k13 = todo_k13_list.pop(0)
        k13.add_k13_to_graph(graph)

        possible_centers = k13.neighbors.copy()
        neighbor_nodes = list(set([y for x in k13.neighbors_edges for y in x]))
        possible_centers.extend(neighbor_nodes)
        # Remove duplicate nodes, and the old center
        possible_centers = list(set(possible_centers))

        degree_3_possible_centers = [v for v in possible_centers if graph.degree[v] == 3]

        new_k13s_found = False

        for combination in list(itertools.combinations(degree_3_possible_centers, 2)):
            v_neighbors = [neighbor for neighbor in graph.neighbors(combination[0])]
            w_neighbors = [neighbor for neighbor in graph.neighbors(combination[1])]

            # Check if they have overlapping neighbors or centers as neighbors, which is not allowed
            if not len(intersection(v_neighbors, w_neighbors)) > 0 \
                    and combination[0] not in w_neighbors \
                    and combination[1] not in v_neighbors:
                v_k13 = K13(combination[0], v_neighbors, graph)
                w_k13 = K13(combination[1], w_neighbors, graph)
                new_k13s_found = True
                break

        if new_k13s_found:
            v_k13.remove_k13_from_graph(graph)
            w_k13.remove_k13_from_graph(graph)
            todo_k13_list.append(v_k13)
            todo_k13_list.append(w_k13)
            optimized_k13_list.append(v_k13)
            optimized_k13_list.append(w_k13)
        else:
            optimized_k13_list.append(k13)

    return optimized_k13_list


def create_flow_graph(k13_list):
    """
    Create a flow graph for the K13s and their possible grandchildren.
    :param k13_list: The list of K13s
    :return: A graph containing the flow network using the K13s and their possible grandchildren
    """
    flow_graph = nx.Graph()
    flow_graph.add_node('source')
    flow_graph.add_node('target')
    grandchildren = []

    for k13 in k13_list:
        flow_graph.add_node(f"k13_{k13.center}")
        flow_graph.add_edge('source', f"k13_{k13.center}")
        flow_graph.add_nodes_from(k13.get_k13_grandchildren())

        for grandchild in k13.get_k13_grandchildren():
            grandchildren.append(grandchild)
            flow_graph.add_edge(f"k13_{k13.center}", grandchild)
            flow_graph.add_edge(grandchild, 'target', capacity=1)

    for grandchild in grandchildren:
        gc_parents = [n for n in flow_graph.neighbors(grandchild) if n != 'target']

        for gc_parent in gc_parents:
            flow_graph[gc_parent][grandchild]['capacity'] = 1 / len(gc_parents)

    for k13 in k13_list:
        k13_node = f"k13_{k13.center}"
        k13_children = [n for n in flow_graph.neighbors(k13_node) if n != 'source']

        capacity = 0
        for k13_child in k13_children:
            capacity += flow_graph[k13_node][k13_child]['capacity']
        flow_graph['source'][k13_node]['capacity'] = capacity

    return flow_graph


def assign_flow_vertices_to_k13(k13_list, flow_graph):
    """
    Assign possible grandchildren to the K13s.
    :param k13_list: The list of K13s
    :param flow_graph: A graph containing the flow network
    :return: List of K13s with grandchildren assigned
    """
    max_flow_result = nx.maximum_flow(flow_graph, _s='source', _t='target')

    for k13 in k13_list:
        grandchildren = max_flow_result[1][f"k13_{k13.center}"]

        for grandchild in grandchildren:
            if grandchildren[grandchild] == 1:
                k13.tree_grandchildren.append(grandchild)

    return k13_list
