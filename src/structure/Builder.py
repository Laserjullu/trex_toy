import networkx as nx
from src.dummy.dummy_louds import DummyLouds, TreeNode
from src.dummy.dummy_wavelet import DummyWaveletTree
from src.dummy.dummy_bitvector import DummyBitvector
from structure.DirectedTrexGraph import DirectedTrexGraph
from structure.UndirectedTrexGraph import UndirectedTrexGraph
import math


class Builder:

    def __init__(self):
        pass


    def build(self, G: nx.DiGraph):

        if isinstance(G, nx.DiGraph):
            return self.build_directed(G)
        if isinstance(G, nx.Graph):
            return self.build_undirected(G)

        
    def build_directed(self, G: nx.DiGraph) -> DirectedTrexGraph:
        
        # we determine the weights by taking the lower indegree of both target vertices, if existing.
        G_undirected = G.to_undirected()
        for u, v in G.edges():
            weight = G.in_degree(v)
            if G.has_edge(v, u):
                weight = min(G.in_degree(u), weight)
            G_undirected[u][v]['weight'] = weight

        # we create a new Graph in which we later remove all the edges, such that we still have the original graph stored. 
        G_minus_T = G.copy()
        roots = []
        new_names = {}
        subgraphs = []
        forest = nx.Graph()

        # now we create spanning Trees for all the subgraphs and store them in one forest, we also remember each subgraph as well as the accoring root.
        for component in nx.connected_components(G_undirected):

            subgraph = G_undirected.subgraph(component)
            Tree = nx.minimum_spanning_tree(subgraph)
            subgraphs.append(Tree)
            # arbitrary root choice for each weak component
            roots.append(list(Tree.nodes())[0])
            forest.add_edges_from(Tree.edges())

        # we add this super root, such that we can run bfs on the forest for renaming
        forest.add_node("super_root")
        for root in roots:
            forest.add_edge("super_root", root)

        nodes = {}
        forest_roots = []
        D = [0] * len(G.nodes())

        i = 1
        # simple bfs for renaming and extraction, where we also remembering the mapping and determining D, we don't need the inverse mapping, 
        # because we can use .items() to later have access to it. 
        bfs_edges = nx.bfs_edges(forest, "super_root")
        for parent, child in bfs_edges:
            if parent == "super_root":
                new_names[child] = i
                nodes[child] = TreeNode()
                forest_roots.append(nodes[child])      
            else: 
                new_names[child] = i
                nodes[child] = TreeNode()
                nodes[parent].children.append(nodes[child])
                
                if G.has_edge(parent, child):
                    D[i - 1] = 1
                    G_minus_T.remove_edge(parent, child)
                else: 
                    G_minus_T.remove_edge(child, parent)
            i += 1


        A_prime = []
        S_prime = []

        # creation of A_prime and S_prime, we implicitly get all the original namings in the right order. 
        for original, i in new_names.items():
   
            outneighbors = list(G_minus_T.successors(original))

            for neighbor in outneighbors:
                A_prime.append(new_names[neighbor])
            
            S_prime.append(1)
            S_prime.extend([0] * len(outneighbors))

        # extra dummy bit for end because we i.e ask for number of outneighbors in A_prime, for which the last 1 makes handling easier
        S_prime.append(1)

        T = DummyLouds(forest_roots)
        A_prime = DummyWaveletTree(A_prime)
        S_prime = DummyBitvector(S_prime)
        D = DummyBitvector(D) 



        # entropy calculation
        m = G.number_of_edges()
        G_entropy_bitvector = 0
        n  = len(G.nodes())
        G_array_entropy = m * math.ceil(math.log2(n)) + n * math.ceil(math.log2(m))

        

        for v in G.nodes():
            indegree = G.in_degree(v)
            if indegree > 0:
                G_entropy_bitvector += indegree * math.log2(m/indegree)
        G_entropy_bitvector += math.log2(math.comb(m + n, n))





        reduced_entropy = 0
        for v in G_minus_T.nodes():
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_entropy += indegree * math.log2(m/indegree)
        reduced_entropy += 3* G_minus_T.number_of_nodes() + math.log2(math.comb(m, G_minus_T.number_of_nodes()))

        entropy_tuple = [G_array_entropy, G_entropy_bitvector, reduced_entropy]


        # makes testing a lot easier
        if len(new_names) > 50:
            new_names = {}

        return DirectedTrexGraph(T, A_prime, S_prime, D, entropy_tuple, len(roots), sorted(new_names.items()))
    




    def build_undirected(self, G: nx.Graph) -> UndirectedTrexGraph: 
        G_directed = nx.DiGraph()
        G_mst = nx.Graph()

        # keeping the direction, that has the higher target degree
        for u, v in G.edges():
            weight = max(G.degree(v), G.degree(u))

            G_mst.add_edge(u,v, weight = weight)
            if G.degree(v) > G.degree(u):
                G_directed.add_edge(u,v)
            else:
                G_directed.add_edge(v,u)


        
        G_minus_T = G.copy()
        roots = []
        new_names = {}
        subgraphs = []
        forest = nx.Graph()

        
        for component in nx.connected_components(G_mst):

            subgraph = G_mst.subgraph(component)
            Tree = nx.minimum_spanning_tree(subgraph)
            subgraphs.append(Tree)
            roots.append(list(Tree.nodes())[0])
            forest.add_edges_from(Tree.edges())


        forest.add_node("super_root")
        for root in roots:
            forest.add_edge("super_root", root)

        nodes = {}
        forest_roots = []
        D = [0] * len(G.nodes())

        i = 1
        bfs_edges = nx.bfs_edges(forest, "super_root")
        
        for parent, child in bfs_edges:
            if parent == "super_root":
                new_names[child] = i
                nodes[child] = TreeNode()
                forest_roots.append(nodes[child])    
            else:
                new_names[child] = i
                nodes[child] = TreeNode()
                nodes[parent].children.append(nodes[child])

                if G_directed.has_edge(parent, child):
                    G_directed.remove_edge(parent, child)
                else:
                    G_directed.remove_edge(child, parent)
            i += 1

        A_prime = []
        S_prime = []

        # creation of A_prime and S_prime, we implicitly get all the original namings in the right order. 
        for original, i in new_names.items():
   
            outneighbors = list(G_directed.successors(original))

            for neighbor in outneighbors:
                A_prime.append(new_names[neighbor])
            
            S_prime.append(1)
            S_prime.extend([0] * len(outneighbors))

        # extra dummy bit for end because we i.e ask for number of outneighbors in A_prime, for which the last 1 makes handling easier
        S_prime.append(1)

        T = DummyLouds(forest_roots)
        A_prime = DummyWaveletTree(A_prime)
        S_prime = DummyBitvector(S_prime)



        # entropy calculation 
        m = G.number_of_edges()
        G_entropy_bitvector = 0
        n  = len(G.nodes())
        G_array_entropy = m * math.ceil(math.log2(n)) + n * math.ceil(math.log2(m))

        

        for v in G.nodes():
            degree = G.degree(v)
            if degree > 0:
                G_entropy_bitvector += degree * math.log2(m/degree)
        G_entropy_bitvector += math.log2(math.comb(m + n, n))





        reduced_entropy = 0
        for v in G_directed.nodes():
            indegree = G_directed.in_degree(v)
            if indegree > 0:
                reduced_entropy += indegree * math.log2(m/indegree)
        reduced_entropy += 3* G_directed.number_of_nodes() + math.log2(math.comb(m, G_directed.number_of_nodes()))

        entropy_tuple = [G_array_entropy, G_entropy_bitvector, reduced_entropy]


        # makes testing a lot easier
        if len(new_names) > 50:
            new_names = {}

        return UndirectedTrexGraph(T, A_prime, S_prime, entropy_tuple, len(roots),sorted(new_names.items()))


