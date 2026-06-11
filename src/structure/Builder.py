import networkx as nx
from src.dummy.dummy_louds import DummyLouds, TreeNode
from src.dummy.dummy_wavelet import DummyWaveletTree
from src.dummy.dummy_bitvector import DummyBitvector
from structure.DirectedTrexGraph import DirectedTrexGraph
from structure.UndirectedTrexGraph import UndirectedTrexGraph
import math
from src.functions.density import density_greedy
from networkx.utils import UnionFind
from tqdm import tqdm
import time
import numpy as np


class Builder:

    def __init__(self):
        pass


    def build(self, G, planar: bool = False):
        if planar:
                return self.build_planar(G)
        else: 
            if isinstance(G, nx.DiGraph):
                return self.build_directed(G)
            if isinstance(G, nx.Graph):
                return self.build_undirected(G)
    

        
    def build_directed(self, G: nx.DiGraph) -> DirectedTrexGraph:
        
        # we determine the weights by taking the lower indegree of both target vertices, if existing.
        print("making it undirected" + str(time.time()))
        G_undirected = G.to_undirected()
        print("finished the undirected version" + str(time.time()))
        for u, v in G.edges():
            weight = G.in_degree(v)
            if G.has_edge(v, u):
                weight = min(G.in_degree(u), weight)
            G_undirected[u][v]['weight'] = weight

        # we create a new Graph in which we later remove all the edges, such that we still have the original graph stored. 
        G_minus_T = G.copy()
        roots = []
        new_names = {}
        forest = nx.Graph()


        components = list(nx.connected_components(G_undirected))
        # now we create spanning Trees for all the subgraphs and store them in one forest, we also remember a root for each Tree
        for component in tqdm(components, total = len(components)):

            subgraph = G_undirected.subgraph(component)
            Tree = nx.minimum_spanning_tree(subgraph)
            # arbitrary root choice for each weak component
            roots.append(list(Tree.nodes())[0])
            forest.add_edges_from(Tree.edges())

        del G_undirected
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
        bfs_edges_list = list(bfs_edges)
        del forest

        for parent, child in tqdm(bfs_edges_list, total = len(bfs_edges_list)):
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
        for original, i in tqdm(new_names.items(), total = len(new_names.items())):
   
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
        
        entropy_tuple, alpha_16, non_zero_indegrees, upper_bound_16, upper_bound_17, indegree_variance, num_classes = self.directed_metrics(G, G_minus_T)

        # makes testing a lot easier
        if len(new_names) > 1000:
            new_names = {}

        return DirectedTrexGraph(T, A_prime, S_prime, D, entropy_tuple, len(roots), alpha_16, non_zero_indegrees, upper_bound_16, upper_bound_17, indegree_variance, num_classes, sorted(new_names.items()))
    

    def build_undirected(self, G: nx.Graph) -> UndirectedTrexGraph: 
        G_minus_T = nx.DiGraph()
        # the undirected graph for the spanning Tree
        G_mst = nx.Graph()

        # important , such that also isolated nodes are added
        G_minus_T.add_nodes_from(G.nodes())
        G_mst.add_nodes_from(G.nodes())
        # keeping the direction, that has the higher target degree
        for u, v in G.edges():
            weight = max(G.degree(v), G.degree(u))

            G_mst.add_edge(u,v, weight = weight)
            if G.degree(v) > G.degree(u):
                G_minus_T.add_edge(u,v)
            else:
                G_minus_T.add_edge(v,u)

        G_greedy = G_minus_T.copy()


    
        roots = []
        new_names = {}
        forest = nx.Graph()

        
        for component in nx.connected_components(G_mst):

            subgraph = G_mst.subgraph(component)
            Tree = nx.minimum_spanning_tree(subgraph)
            roots.append(list(Tree.nodes())[0])
            forest.add_edges_from(Tree.edges())


        forest.add_node("super_root")
        for root in roots:
            forest.add_edge("super_root", root)

        nodes = {}
        forest_roots = []

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

                if G_minus_T.has_edge(parent, child):
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

        entropy_tuple, alpha_16, non_zero_indegrees, upper_bound_16, upper_bound_17, indegree_variance, num_classes = self.undirected_metrics(G, G_minus_T, G_greedy)

        
        return UndirectedTrexGraph(T, A_prime, S_prime, entropy_tuple, len(roots), alpha_16, non_zero_indegrees, upper_bound_16, upper_bound_17, indegree_variance, num_classes, sorted(new_names.items()))
    

    def build_planar(self, G):
        if isinstance(G, nx.DiGraph):   
            G_built = self.build(G)
            G_undirected = G.to_undirected()

            for u, v in G.edges():
                weight = G.in_degree(v)
                if G.has_edge(v, u):
                    weight = min(G.in_degree(u), weight)
                G_undirected[u][v]['weight'] = weight
            
            planar_edges, G_prime = self.extract_planar_edges(G_undirected, G.copy(), G)
            
            planar_entropy = 0
            m_dash = G_prime.number_of_edges()
            for v in G_prime.nodes():
                indegree = G_prime.in_degree(v)
                if indegree > 0:
                    planar_entropy += indegree * math.log2(m_dash/indegree)
            planar_entropy += 2.092 * G.number_of_nodes() + len(planar_edges) + math.log2(math.comb(m_dash + G_prime.number_of_nodes(), G_prime.number_of_nodes()))


            G_built.entropy_tuple[3] = planar_entropy
        
            return G_built

        elif isinstance(G, nx.Graph):
            G_built = self.build(G)
            G_prime = nx.DiGraph()
            G_prime.add_nodes_from(G.nodes())
            G_undirected = G.copy()
            for u, v in G.edges():
                weight = max(G.degree(v), G.degree(u))
                G_undirected[u][v]['weight'] = weight
                if G.degree(v) > G.degree(u):
                    G_prime.add_edge(u,v)
                else:
                    G_prime.add_edge(v,u)
            planar_edges, G_prime = self.extract_planar_edges(G_undirected, G_prime)

    

            planar_entropy = 0
            m_dash = G_prime.number_of_edges()
            for v in G_prime.nodes():
                indegree = G_prime.in_degree(v)
                if indegree > 0:
                    planar_entropy += indegree * math.log2(m_dash/indegree)
            # 2.5 because we leave out the edges for the direction bitvector.
            planar_entropy += 2.092 * G.number_of_nodes() + math.log2(math.comb(m_dash + G_prime.number_of_nodes(), G_prime.number_of_nodes()))


            G_built.entropy_tuple[5] = planar_entropy

            return G_built

    def extract_planar_edges(self, G_undirected: nx.Graph, G_prime: nx.DiGraph, G_original: nx.DiGraph = None):
        union_find = UnionFind()
        planar_edges = set()
        triangles = []
        # Finding all triangles 
        for u in G_undirected.nodes():
            u_neighbors = set(G_undirected.neighbors(u))
            for v in u_neighbors:
                both_neighbors = u_neighbors.intersection(G_undirected.neighbors(v))
                for w in both_neighbors:
                    # making sure that there are no duplicates
                    if v<w<u: 
                        triangle_weight = G_undirected[u][v]["weight"] + G_undirected[v][w]["weight"] + G_undirected[w][u]["weight"]
                        triangles.append((triangle_weight, u, v, w))
                
        for (triangle_weight, u, v, w) in sorted(triangles):
            if union_find[u] != union_find[v] and union_find[v] != union_find[w] and union_find[u] != union_find[w]:

                    if G_prime.has_edge(u,v) and not G_prime.has_edge(v,u):
                        planar_edges.add((u,v))
                        G_prime.remove_edge(u,v)
                    elif G_prime.has_edge(v,u) and not G_prime.has_edge(u,v):
                        planar_edges.add((v,u))
                        G_prime.remove_edge(v,u)
                    else:
                        if G_original.in_degree(u) > G_original.in_degree(v):
                            planar_edges.add((u,v))
                            G_prime.remove_edge(u,v)
                        else:
                            planar_edges.add((v,u))
                            G_prime.remove_edge(v,u)
                    
                    if G_prime.has_edge(v,w) and not G_prime.has_edge(w,v):
                        planar_edges.add((v,w))
                        G_prime.remove_edge(v,w)
                    elif G_prime.has_edge(w,v) and not G_prime.has_edge(v,w):
                        planar_edges.add((w,v))
                        G_prime.remove_edge(w,v)
                    else:
                        if G_original.in_degree(v) > G_original.in_degree(w):
                            planar_edges.add((v,w))
                            G_prime.remove_edge(v,w)
                        else:
                            planar_edges.add((w,v))
                            G_prime.remove_edge(w,v)

                    if G_prime.has_edge(w,u) and not G_prime.has_edge(u,w):
                        planar_edges.add((w,u))
                        G_prime.remove_edge(w,u)
                    elif G_prime.has_edge(u,w) and not G_prime.has_edge(w,u):
                        planar_edges.add((u,w))
                        G_prime.remove_edge(u,w)
                    else: 
                        if G_original.in_degree(w) > G_original.in_degree(u):
                            planar_edges.add((w,u))
                            G_prime.remove_edge(w,u)
                        else:
                            planar_edges.add((u,w))
                            G_prime.remove_edge(u,w)
                    union_find.union(u,v)
                    union_find.union(v,w)
                    union_find.union(u,w)

        # adding remaining edges, which are not in a triangle

        def weight_key(edge):
            return G_undirected[edge[0]][edge[1]]["weight"]
            
        for u, v in sorted(G_undirected.edges(), key = weight_key):
            # check if edge has already been removed
            if not G_prime.has_edge(u,v) and not G_prime.has_edge(v,u):
                continue

            if union_find[u] != union_find[v]:
                if G_prime.has_edge(u,v) and not G_prime.has_edge(v,u):
                    planar_edges.add((u,v))
                    G_prime.remove_edge(u,v)
                elif G_prime.has_edge(v,u) and not G_prime.has_edge(u,v):
                    planar_edges.add((v,u))
                    G_prime.remove_edge(v,u)
                else:
                    if G_original.in_degree(u) > G_original.in_degree(v):
                        planar_edges.add((u,v))
                        G_prime.remove_edge(u,v)
                    else:
                        planar_edges.add((v,u))
                        G_prime.remove_edge(v,u)
                union_find.union(u,v)
        return planar_edges, G_prime

    def directed_metrics(self, G: nx.DiGraph, G_minus_T: nx.DiGraph):
         # entropy calculation
        m = G.number_of_edges()
        G_entropy_bitvector = 0
        n  = len(G.nodes())
        if m == 0:
            G_array_entropy = 0
        else:
            G_array_entropy = m * math.ceil(math.log2(n)) + n * math.ceil(math.log2(m))

        

        for v in tqdm(G.nodes(), total = len(G.nodes())):
            indegree = G.in_degree(v)
            # already includes the case of m == 0
            if indegree > 0:
                G_entropy_bitvector += indegree * math.log2(m/indegree)
        G_entropy_bitvector += math.log2(math.comb(m + n, n))





        reduced_entropy = 0
        reduced_indegree_entropy = 0
        m_dash = G_minus_T.number_of_edges()
        for v in tqdm(G_minus_T.nodes(), total = len(G_minus_T.nodes())):
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_indegree_entropy += indegree * math.log2(m_dash/indegree)
        reduced_entropy += reduced_indegree_entropy + 3* G_minus_T.number_of_nodes() + math.log2(math.comb(m_dash + G_minus_T.number_of_nodes(), G_minus_T.number_of_nodes()))

        # extra zero in case planar is added later on. 
        entropy_tuple = [G_array_entropy, G_entropy_bitvector, reduced_entropy, -1]

        start = time.time()
        # calculating alpha 
        G_multigraph = nx.MultiGraph()
        # need to manually add the edges, otherwise only one direction is added. 
        G_multigraph.add_edges_from(G.edges)
        G_multigraph.add_nodes_from(G.nodes)
        
        # choosing 13 Iterations, because in Boob et al's Paper it took 12.69 iterations to reach the optimum on avg. 
        print("beginning of Greedy alpha determination: ")
        start = time.time()
        G_prime_density = density_greedy(G_multigraph, 13)[0]
        del G_multigraph

        G_density = G.number_of_edges() / G.number_of_nodes()
        alpha_16 = G_prime_density / G_density
        print("Greedy took: " + str(time.time() - start))



        H_indegree = 0
        if m > 0:
            H_indegree = (entropy_tuple[1] - math.log2(math.comb(m+n,n)))/m
        

        H_indegree_entropy = H_indegree * m 
        upper_bound_16 = H_indegree_entropy - ((n)/(2 * alpha_16)) * H_indegree + (2* n)/math.log(2)

        non_zero_indegrees = 0
        for v in G.nodes():
            if G.in_degree(v) > 0:
                non_zero_indegrees += 1
        
        alpha_17 = n /non_zero_indegrees
        upper_bound_17 = H_indegree_entropy - ((n)/(2 * alpha_17)) * H_indegree + (2* n)/math.log(2)

        indegrees = []
        for v in G.nodes(): 
            indegrees.append(G.in_degree(v))
        indegree_variance = np.var(indegrees)

        # number of theoretical twin classes 
        twin_classes = {}
        for v in G.nodes():
            in_neighbors = tuple(sorted(G.predecessors(v)))
            out_neighbors = tuple(sorted(G.successors(v)))
            neighbors = (in_neighbors, out_neighbors)
            if neighbors not in twin_classes:
                twin_classes[neighbors] = []
                twin_classes[neighbors].append(v)

        num_classes = len(twin_classes)
        



        return entropy_tuple, alpha_16, non_zero_indegrees, upper_bound_16, upper_bound_17, indegree_variance, num_classes

    def undirected_metrics(self, G: nx.Graph, G_minus_T: nx.Graph, G_greedy: nx.DiGraph):
        
        # entropy calculation 
        m = G.number_of_edges()
        G_entropy_bitvector_greedy = 0
        G_entropy_bitvector_random = 0
        G_entropy_bitvector = 0
        n  = len(G.nodes())
        if m == 0:
            G_array_entropy = 0
        else:
            # essentailly just double the edges when represented as a basic edgelist. 
            G_array_entropy = 2 * m * math.ceil(math.log2(n)) + n * math.ceil(math.log2(2 * m))


        for v in G_greedy.nodes():
            indegree = G_greedy.in_degree(v)
            if indegree > 0:
                G_entropy_bitvector_greedy += indegree * math.log2(m/indegree)
        G_entropy_bitvector_greedy += math.log2(math.comb(m + n, n))

        for v in G.nodes():
            degree = G.degree(v)
            if degree > 0:
                G_entropy_bitvector += degree * math.log2(m/degree)
        G_entropy_bitvector += math.log2(math.comb(m + n, n))
        
        G_random = G.to_directed()
        for u, v in G.edges():
            if u < v: 
                G_random.remove_edge(u,v)
        
        for v in G_random.nodes():
            indegree = G_random.in_degree(v)
            if indegree > 0:
                G_entropy_bitvector_random += indegree * math.log2(m/indegree)
        G_entropy_bitvector_random += math.log2(math.comb(m + n, n))        
        
        reduced_entropy = 0
        reduced_indegree_entropy = 0
        m_dash = G_minus_T.number_of_edges()
        for v in G_minus_T.nodes():
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_indegree_entropy += indegree * math.log2(m_dash/indegree)
        
        reduced_entropy += reduced_indegree_entropy + 2* G_minus_T.number_of_nodes() + math.log2(math.comb(m_dash + G_minus_T.number_of_nodes(), G_minus_T.number_of_nodes()))

        entropy_tuple = [G_array_entropy, G_entropy_bitvector, G_entropy_bitvector_random, G_entropy_bitvector_greedy, reduced_entropy, -1]

        start = time.time()

        G_prime_density = density_greedy(G, 13)[0]

        G_density = G.number_of_edges() / G.number_of_nodes()
        alpha_16 = G_prime_density / G_density
        print("Greedy took: " + str(time.time() - start))

        H_indegree = 0
        if m > 0: 
            # we take the the greedy approach to compare with the bound 
            H_indegree_entropy_per_edge = (entropy_tuple[3] - math.log2(math.comb(m+n, n)))/m

        H_indegree_entropy = H_indegree * m 
        upper_bound_16 = H_indegree_entropy - ((n)/(2 * alpha_16)) * H_indegree_entropy_per_edge + (2* n)/math.log(2)

        non_zero_indegrees = 0
        for v in G_greedy.nodes():
            if G_greedy.in_degree(v) > 0:
                non_zero_indegrees += 1
        
        alpha_17 = n/non_zero_indegrees
        upper_bound_17 = H_indegree_entropy - ((n)/(2 * alpha_17)) * H_indegree + (2* n)/math.log(2)

        indegrees = []
        for v in G_greedy.nodes():
            indegrees.append(G_greedy.in_degree(v))
        indegree_variance = np.var(indegrees) if len(indegrees) > 0 else 0.0

        twin_classes = {}
        for v in G.nodes():
            neighbors = tuple(sorted(G.neighbors(v)))
            if neighbors not in twin_classes: 
                twin_classes[neighbors] = []
                twin_classes[neighbors].append(v)
        num_classes = len(twin_classes)

        return entropy_tuple, alpha_16, non_zero_indegrees, upper_bound_16, upper_bound_17, indegree_variance, num_classes


        


