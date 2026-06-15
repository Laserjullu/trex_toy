from src.structure.Builder import Builder
import networkx as nx
import random
import sys
import unittest
class TestAutomated(unittest.TestCase):
    def check_directed_graph(self, G: nx.DiGraph):
        builder = Builder()
        graph, G_minus_T = builder.build(G)

        node_map = dict(graph.new_names)
        inverse_map = {}
        for old, new in graph.new_names:
            inverse_map[new] = old

        for node in G.nodes():
            new_node = node_map[node]


            self.assertEqual(graph.outdegree(new_node), G.out_degree(node))
            self.assertEqual(graph.indegree(new_node), G.in_degree(node))

            G_outgoing = set()
            G_ingoing = set()
            graph_outgoing = set()
            graph_ingoing = set()
            
            for node_dash in G.nodes():
                new_node_dash = node_map[node_dash]

                self.assertEqual(G.has_edge(node, node_dash), graph.is_edge(new_node, new_node_dash))
                G_adjacent = False
                if G.has_edge(node, node_dash):
                    G_adjacent = True
                    G_outgoing.add(node_dash)
                if G.has_edge(node_dash, node):
                    G_adjacent = True
                    G_ingoing.add(node_dash)
                self.assertEqual(G_adjacent, graph.adjacent(new_node, new_node_dash))

            for i in range (1, graph.outdegree(new_node ) + 1):
                outneighbor = graph.outneighbor(new_node, i)
                outneighbor_original = inverse_map[outneighbor]
                graph_outgoing.add(outneighbor_original)
            
            for i in range (1, graph.indegree(new_node) + 1):
                inneighbor = graph.inneighbor(new_node, i)
                inneighbor_original = inverse_map[inneighbor]
                graph_ingoing.add(inneighbor_original)

            self.assertEqual(G_outgoing, graph_outgoing)
            self.assertEqual(G_ingoing, graph_ingoing)

    def check_undirected_graph(self, G: nx.Graph):
        builder = Builder()
        graph, G_minus_T, G_greedy = builder.build(G)

        node_map = dict(graph.new_names)
        inverse_map = {}
        for old, new in graph.new_names:
            inverse_map[new] = old

        for node in G.nodes():
            new_node = node_map[node]

            self.assertEqual(graph.degree(new_node), G.degree(node))
            
            G_neighbors = set(G.neighbors(node))
            graph_neighbors = set()

            for node_dash in G.nodes():
                new_node_dash = node_map[node_dash]

                self.assertEqual(G.has_edge(node, node_dash), graph.adjacent(new_node, new_node_dash))

            for i in range(1, graph.degree(new_node) +1):
                neighbor = graph.neighbor(new_node, i)
                neighbor_original = inverse_map[neighbor]
                graph_neighbors.add(neighbor_original)
            
            self.assertEqual(G_neighbors, graph_neighbors)


    def run_automated(self, number: int):
        for i in range(number):
            G = nx.erdos_renyi_graph(random.randint(1, 100), random.random(), directed = True)
            self.check_directed_graph(G)
        for i in range(number):
            G = nx.erdos_renyi_graph(random.randint(1, 100), random.random(), directed = False)
            self.check_undirected_graph(G)

        print("all automated tests passed")


        
    def complete_test(self, number: int):

        self.run_automated(number)
        
        empty_undirected = nx.empty_graph(10)
        empty_directed = empty_undirected.to_directed()
        dense_undirected = nx.complete_graph(10)
        dense_directed = dense_undirected.to_directed()


        self.check_undirected_graph(empty_undirected)
        self.check_directed_graph(empty_directed)
        self.check_undirected_graph(dense_undirected)
        self.check_directed_graph(dense_directed)

    def test_all(self):
        self.complete_test(10)
