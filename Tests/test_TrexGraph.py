import unittest


from structure.DirectedTrexGraph import DirectedTrexGraph
from structure.UndirectedTrexGraph import UndirectedTrexGraph
from src.structure.Builder import Builder
import networkx as nx
import math 
class test_TrexGraph(unittest.TestCase):

    
    def test_TrexGraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (1, 3), (2, 3), (3, 1), (1, 4)])
        b = Builder()
        graph, G_minus_T= b.build(G)
    
        total_outdegree = 0
        total_indegree = 0
        for v in range(1, len(G.nodes) + 1):
            total_outdegree += graph.outdegree(v)
            total_indegree += graph.indegree(v)

        self.assertTrue(total_outdegree == G.number_of_edges())
        self.assertTrue(graph.outdegree(1) == 3)

        self.assertTrue(total_indegree == G.number_of_edges())
        self.assertTrue(graph.indegree(1) == 1)

        self.assertTrue(graph.adjacent(1,2))
        self.assertFalse(graph.adjacent(4,3))

        # by chance the names stayed the same after renaming, therefore the test should work
        print(str(graph.outneighbor(1, 1)))
        print(str(graph.outneighbor(1, 3)))
        print(str(graph.outneighbor(3, 1)))

        print(str(graph.inneighbor(1,2)))

        print("outneighbor_ranks for vertice 1: ")
        print(str(graph.outneighbor_rank(1, 2)))
        print(str(graph.outneighbor_rank(1, 4)))
        print(str(graph.outneighbor_rank(1, 3)))

        print(str(graph.outneighbor_rank(2, 3)))


        print("inneighbor ranks for node 1:")
        print(str(graph.inneighbor_rank(2, 3)))



        print("Passed! :)")

        graph.print()

        print("second experimental part starts here, undirected Karate: \n \n \n ")

        G = nx.karate_club_graph()
        b = Builder()
        karate, G_minus_T, G_greedy= b.build(G)

        karate.print()

        print(str(karate.adjacent(26, 16)))
        print(str(karate.adjacent(6,13)))
        print(str(karate.adjacent(6, 1)))
        print(str(karate.degree(4)))


        print("\n \n Bad example: \n")

        bad_G = nx.DiGraph()
   
        bad_G.add_edges_from([(i, j) for i in range(1, 101) for j in range(1, 101)])
      
        bad_trex_graph, G_minus_T = b.build(bad_G)
        bad_trex_graph.print()

        print("\n \n Good example: \n")
        
        good_G = nx.DiGraph()
        
        good_G.add_edges_from([(1, v) for v in range(2, 101)])
        optimal_trex_graph, G_minus_T= b.build(good_G)
        optimal_trex_graph.print()

        print("\n\nSame Karate Graph, but undirected this time:\n")
        G = nx.karate_club_graph()
        b = Builder()
        karate, G_minus_T, G_greedy = b.build(G)

        karate.print()



        G = nx.DiGraph()
        G.add_edges_from([(1, 2), (2, 1), (3, 4), (4, 3)])
        b = Builder()
        graph, G_minus_T = b.build(G)
        graph.print()
        print(str(graph.outdegree(2)))
        print(str(graph.outdegree(3)))
        print(str(graph.outdegree(1)))
        print(str(graph.outdegree(4)))

if __name__ == '__main__':
    unittest.main()


