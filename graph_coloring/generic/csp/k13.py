import itertools
import math

import networkx as nx

from graph_coloring.misc import get_vertices_of_degree_n, intersection


class K13:
    """Class representing a K1,3 instance."""
    center: str
    children: list
    children_edges: list
    grandchildren: list

    def __init__(self, center, children, graph):
        self.center = center
        self.children = children
        self.children_edges = []
        self.grandchildren = []

        for child in children:
            self.children_edges.extend(
                [edge for edge in graph.edges([child]) if edge[0] != center and edge[1] != center])

    def check_if_k13_exists(self, graph: nx.Graph):
        """
        Check if this K13 exists in the given graph.
        :param graph: Graph to check if it contains this K13
        :return: True if given graph contains this K13, False else
        """
        if len(self.children) != 3:
            raise Exception('A K1,3 must contain exactly 3 neighbors.')

        return graph.has_node(self.center) \
            and graph.has_node(self.children[0]) \
            and graph.has_node(self.children[1]) \
            and graph.has_node(self.children[2])

    def get_k13_edges(self):
        """
        Get all internal edges of this K13.
        :return: List of edges
        """
        return [(self.center, child) for child in self.children]

    def remove_k13_from_graph(self, graph: nx.Graph):
        """
        Remove K13 from the given graph.
        :param graph: Graph to be removed from
        """
        graph.remove_node(self.center)
        graph.remove_nodes_from(self.children)

    def add_k13_to_graph(self, graph: nx.Graph):
        """
        Add K13 to the given graph.
        :param graph: Graph to be added to
        """
        graph.add_node(self.center)
        graph.add_nodes_from(self.children)
        graph.add_edges_from(self.get_k13_edges())
        graph.add_edges_from(self.children_edges)

    def get_k13_children_neighbors(self):
        """
        Get the neighbors of the children of this K13.
        :return: List of unique neighbors
        """
        neighbor_vertices = []

        for neighbor_edge in self.children_edges:
            if neighbor_edge[0] in self.children:
                neighbor_vertices.append(neighbor_edge[1])
            else:
                neighbor_vertices.append(neighbor_edge[0])

        return list(set(neighbor_vertices))

    def get_children_dict(self):
        """
        Get the dict of all children of the K13 (so only center).
        :return: Dict of children
        """
        return {self.center: self.children}

    def get_all_nodes(self):
        """
        Get all internal nodes of the K13.
        :return: List of all internal nodes
        """
        return [self.center] + self.children


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


def check_k13_overlap(k13, optimized_k13_list):
    """
    Check for the given K13 if it has overlap with any of the previous K13s.
    :param k13: K13 to check overlap for
    :param optimized_k13_list: List of previous K13s
    :return: Bool whether the K13 has overlap
    """
    # Check that the nodes of this K13 have no overlap with the nodes of other K13s
    overlap_with_previous_k13 = False
    for optimized_k13 in optimized_k13_list:
        optimized_k13_nodes = optimized_k13.get_all_nodes()

        for node in k13.get_all_nodes():
            if node in optimized_k13_nodes:
                overlap_with_previous_k13 = True

    return overlap_with_previous_k13


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

        overlap_with_previous_k13 = check_k13_overlap(k13, optimized_k13_list)

        # Skip this K13
        if overlap_with_previous_k13:
            continue

        possible_centers = k13.children.copy()
        neighbor_nodes = list(set([y for x in k13.children_edges for y in x]))
        possible_centers.extend(neighbor_nodes)
        # Remove duplicate nodes, and the old center
        possible_centers = list(set(possible_centers))

        degree_3_possible_centers = [v for v in possible_centers if graph.degree[v] == 3]

        new_k13s_found = False

        for combination in list(itertools.combinations(degree_3_possible_centers, 2)):
            v_neighbors = list(graph.neighbors(combination[0]))
            w_neighbors = list(graph.neighbors(combination[1]))

            # Check if they have overlapping neighbors or centers as neighbors, which is not allowed
            if not len(intersection(v_neighbors, w_neighbors)) > 0 \
                    and combination[0] not in w_neighbors \
                    and combination[1] not in v_neighbors:
                v_k13 = K13(combination[0], v_neighbors, graph)
                w_k13 = K13(combination[1], w_neighbors, graph)

                v_k13_overlap_with_previous_k13 = check_k13_overlap(v_k13, optimized_k13_list)
                w_k13_overlap_with_previous_k13 = check_k13_overlap(w_k13, optimized_k13_list)

                # Skip this K13 if there is overlap
                if v_k13_overlap_with_previous_k13 or w_k13_overlap_with_previous_k13:
                    continue

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


def floor_flow_capacities(node_capacities, flow_graph):
    """
    Convert the given capacity to a integer capacity by flooring it.
    :param node_capacities: Node and capacity to floor
    :param flow_graph: Flow graph containing the flow network
    """
    for c in node_capacities:
        flow_graph['source'][c[0]]['capacity'] = math.floor(c[1])


def ceil_flow_capacities(node_capacities, flow_graph):
    """
    Convert the given capacity to a integer capacity by ceiling it.
    :param node_capacities: Node and capacity to ceil
    :param flow_graph: Flow graph containing the flow network
    """
    for c in node_capacities:
        flow_graph['source'][c[0]]['capacity'] = math.ceil(c[1])


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

    all_k13s_vertices = [node for k13 in k13_list for node in k13.get_all_nodes()]

    for k13 in k13_list:
        flow_graph.add_node(f"k13_{k13.center}")
        flow_graph.add_edge('source', f"k13_{k13.center}")

        for grandchild in k13.get_k13_children_neighbors():
            # We don't want vertices of other K13s as potential grandchildren
            if grandchild in all_k13s_vertices:
                continue

            flow_graph.add_node(grandchild)
            grandchildren.append(grandchild)
            flow_graph.add_edge(f"k13_{k13.center}", grandchild)
            flow_graph.add_edge(grandchild, 'target', capacity=1)

    for grandchild in grandchildren:
        if grandchild in all_k13s_vertices:
            continue

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

    non_integer_capacities = []

    for k13 in k13_list:
        k13_node = f"k13_{k13.center}"
        source_k13_capacity = flow_graph['source'][k13_node]['capacity']

        if not float(source_k13_capacity).is_integer():
            non_integer_capacities.append((k13_node, source_k13_capacity))

    non_integer_capacities.sort(key=lambda x: x[1])

    # Greedily convert the fractional capacities into integer capacities
    half_integer_capacities = [c for c in non_integer_capacities if c[1] % 1 == 0.5]

    if len(half_integer_capacities) % 2 != 0:
        # TODO the case that we have an uneven number of half integer capacities
        assert False

    less_integer_capacities = [c for c in non_integer_capacities if c[1] % 1 < 0.5]
    more_integer_capacities = [c for c in non_integer_capacities if c[1] % 1 > 0.5]

    floor_flow_capacities(less_integer_capacities, flow_graph)
    ceil_flow_capacities(more_integer_capacities, flow_graph)

    half_to_floor = half_integer_capacities[:len(half_integer_capacities) // 2]
    half_to_ceil = half_integer_capacities[len(half_integer_capacities) // 2:]

    floor_flow_capacities(half_to_floor, flow_graph)
    ceil_flow_capacities(half_to_ceil, flow_graph)

    for k13 in k13_list:
        for grandchild in k13.get_k13_children_neighbors():
            if grandchild in all_k13s_vertices:
                continue

            flow_graph[f"k13_{k13.center}"][grandchild]['capacity'] = 1

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
                k13.grandchildren.append(grandchild)

    return k13_list
