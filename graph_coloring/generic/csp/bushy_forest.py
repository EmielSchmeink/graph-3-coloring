from dataclasses import dataclass

from tqdm import tqdm

from graph_coloring.misc import remove_without_copy, add_nodes_with_edges


@dataclass
class BushyTree:
    """Class representing a bushy tree."""
    root: str
    internal_nodes: list
    leaves: list
    tree_edges: list
    neighbors: list
    neighbors_edges: list

    def get_all_nodes(self):
        """
        Get all nodes inside the bushy tree.
        :return: List of all nodes
        """
        all_nodes = [self.root]
        all_nodes.extend(self.internal_nodes)
        all_nodes.extend(self.leaves)
        return all_nodes

    def get_all_nodes_and_neighbors(self, graph):
        """
        Get all nodes inside the bushy tree and the neighbors of the bushy tree.
        :param graph: Graph in which the neighbors of the bushy tree lie
        :return: List of all nodes (including neighbors)
        """
        all_nodes = [self.root]
        all_nodes.extend(self.internal_nodes)
        all_nodes.extend(self.leaves)
        all_nodes.extend(self.get_neighbor_vertices(graph))
        return all_nodes

    def get_node_neighbors(self, node):
        """
        Get the neighbors of this bushy tree node by the neighbor edges.
        :param node: Node of which the neighbors are retrieved
        :return: List of neighbors of the given node
        """
        neighbors = []
        for edge in self.neighbors_edges:
            if edge[0] == node:
                neighbors.append(edge[1])
            elif edge[1] == node:
                neighbors.append(edge[0])
        return neighbors

    def get_node_children(self, node):
        """
        Get the children of a given node in the bushy tree.
        :param node: Node of which the children are retrieved
        :return: List of children of the given node
        """
        internal_node_children = []
        leaf_children = []
        for edge in self.tree_edges:
            if edge[0] == node:
                if edge[1] in self.leaves:
                    leaf_children.append(edge[1])
                if edge[1] in self.internal_nodes:
                    internal_node_children.append(edge[1])
        return internal_node_children, leaf_children

    def get_node_children_dict(self):
        """
        Get a dict of children for all nodes in the bushy tree.
        :return: Dict with node: children pairs
        """
        root_children = self.get_node_children(self.root)[0] + self.get_node_children(self.root)[1]
        node_children = {self.root: root_children}
        for internal_node in self.internal_nodes:
            all_children_tuple = self.get_node_children(internal_node)
            all_children = all_children_tuple[0] + all_children_tuple[1]
            node_children = node_children | {internal_node: all_children}
        return node_children

    def get_neighbor_vertices(self, graph):
        """
        Get all (and only) neighbor vertices of the bushy tree in the given graph.
        :param graph: Graph in which the neighbors lie
        :return: List of all neighbors for all nodes of the bushy tree
        """
        self.neighbors = []
        self.neighbors.extend([neighbor for neighbor in graph.neighbors(self.root)
                               if neighbor not in self.internal_nodes and neighbor not in self.leaves])

        for leaf in self.leaves:
            self.neighbors.extend([neighbor for neighbor in graph.neighbors(leaf)
                                   if neighbor not in self.root
                                   and neighbor not in self.internal_nodes
                                   and neighbor not in self.leaves])

        return list(set(self.neighbors))

    def get_neighbor_edges(self, graph):
        """
        Get all (and only) neighbor edges of the bushy tree in the given graph.
        :param graph: Graph in which the neighbor edges lie
        :return: List of all neighbor edges for all nodes of the bushy tree
        """
        self.neighbors_edges = []
        self.neighbors_edges.extend([(self.root, neighbor) for neighbor in graph.neighbors(self.root)
                                     if neighbor not in self.internal_nodes and neighbor not in self.leaves])

        for leaf in self.leaves:
            self.neighbors_edges.extend([(leaf, neighbor) for neighbor in graph.neighbors(leaf)
                                         if neighbor not in self.root
                                         and neighbor not in self.internal_nodes
                                         and neighbor not in self.leaves])

        return list(set(self.neighbors_edges))


def get_maximal_bushy_forest(graph):
    """
    Get a maximal bushy forest for a given graph, by fixing a node and then extending it using the rules of the
    bushy tree, until all nodes have been checked if they are part of a bushy tree.
    :param graph: Graph in which the bushy trees must be created
    :return: List of BushyTree
    """
    forest = []

    tqdm_nodes = tqdm(list(graph.nodes()))
    tqdm_nodes.set_description(desc="Looping over nodes for forest", refresh=True)
    graph_without_forest = graph

    for v in tqdm_nodes:
        removed_edges = []

        for tree in forest:
            graph_without_forest, part_removed_edges = remove_without_copy(graph_without_forest, tree.get_all_nodes())
            removed_edges.extend(part_removed_edges)

        if not graph_without_forest.has_node(v):
            add_nodes_with_edges(graph_without_forest, removed_edges)
            continue

        all_nodes = []
        for tree in forest:
            all_nodes.extend(tree.get_all_nodes())

        neighbors = [neighbor for neighbor in graph_without_forest.neighbors(v)]

        if v not in all_nodes and len(neighbors) >= 4:
            neighbors = [neighbor for neighbor in graph_without_forest.neighbors(v) if neighbor not in all_nodes]
            v_edges = [(v, neighbor) for neighbor in neighbors]

            bushy_tree = BushyTree(v, [], neighbors.copy(), v_edges.copy(), [], [])
            forest.append(bushy_tree)

            vertices_to_be_processed = neighbors
            while len(vertices_to_be_processed) > 0:
                w = vertices_to_be_processed.pop(0)

                all_nodes = []
                for tree in forest:
                    all_nodes.extend(tree.get_all_nodes())

                w_neighbors_not_in_forest = [w_neighbor for w_neighbor in graph_without_forest.neighbors(w)
                                             if w_neighbor not in all_nodes]

                # These neighbors should still be recognised as neighbors to make sure there are no conflicting colors
                # later on, since if we do not add these edges, the recursive coloring will not consider them
                w_neighbors_in_forest = [w_neighbor for w_neighbor in graph_without_forest.neighbors(w)
                                         if w_neighbor in all_nodes]

                for neighbor in w_neighbors_in_forest:
                    bushy_tree.tree_edges.append((w, neighbor))

                if len(w_neighbors_not_in_forest) >= 3:
                    bushy_tree.leaves.remove(w)
                    bushy_tree.internal_nodes.append(w)

                    for neighbor in w_neighbors_not_in_forest:
                        bushy_tree.tree_edges.append((w, neighbor))

                    bushy_tree.leaves.extend(w_neighbors_not_in_forest)
                    vertices_to_be_processed.extend(w_neighbors_not_in_forest)

        add_nodes_with_edges(graph_without_forest, removed_edges)

    return forest
