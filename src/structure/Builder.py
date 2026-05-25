import networkx as nx
from src.dummy.dummy_louds import DummyLouds, TreeNode
from src.dummy.dummy_wavelet import DummyWaveletTree
from src.dummy.dummy_bitvector import DummyBitvector
from structure.DirectedTrexGraph import DirectedTrexGraph
from structure.UndirectedTrexGraph import UndirectedTrexGraph
import math
from src.functions.density import density_greedy
from networkx.utils import UnionFind


class Builder:

    def __init__(self):
        pass


    def build(self, G, planar: bool = False):
        if planar and isinstance(G, nx.DiGraph):
            print("Planar entropy is here:)")
            print(self.build_planar(G))
            return self.build_directed(G)
        else: 
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
        forest = nx.Graph()

        # now we create spanning Trees for all the subgraphs and store them in one forest, we also remember a root for each Tree
        for component in nx.connected_components(G_undirected):

            subgraph = G_undirected.subgraph(component)
            Tree = nx.minimum_spanning_tree(subgraph)
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
        if m == 0:
            G_array_entropy = 0
        else:
            G_array_entropy = m * math.ceil(math.log2(n)) + n * math.ceil(math.log2(m))

        

        for v in G.nodes():
            indegree = G.in_degree(v)
            # already includes the case of m == 0
            if indegree > 0:
                G_entropy_bitvector += indegree * math.log2(m/indegree)
        G_entropy_bitvector += math.log2(math.comb(m + n, n))





        reduced_entropy = 0
        m_dash = G_minus_T.number_of_edges()
        for v in G_minus_T.nodes():
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_entropy += indegree * math.log2(m_dash/indegree)
        reduced_entropy += 3* G_minus_T.number_of_nodes() + math.log2(math.comb(m_dash + G_minus_T.number_of_nodes(), G_minus_T.number_of_nodes()))

        # extra zero in case planar is added later on. 
        entropy_tuple = [G_array_entropy, G_entropy_bitvector, reduced_entropy, -1]

        # calculating alpha 
        G_multigraph = nx.MultiGraph()
        # need to manually add the edges, otherwise only one direction is added. 
        G_multigraph.add_edges_from(G.edges)
        G_multigraph.add_nodes_from(G.nodes)
        # choosing 13 Iterations, because in Boob et al's Paper it took 12.69 iterations to reach the optimum on avg. 
        G_prime_density = density_greedy(G_multigraph, 13)[0]
        G_density = G.number_of_edges() / G.number_of_nodes()
        alpha = G_prime_density / G_density


        H_indegree = 0
        if m > 0:
            H_indegree = (entropy_tuple[1] - math.log2(math.comb(m+n,n)))/m

        upper_bound = entropy_tuple[1] - ((n)/(2 * alpha)) * H_indegree + (2* n)/math.log(2)

        normalized_difference = (upper_bound - entropy_tuple[2] )/ ( n * math.log2(n))

        # makes testing a lot easier
        if len(new_names) > 1000:
            new_names = {}

        return DirectedTrexGraph(T, A_prime, S_prime, D, entropy_tuple, len(roots), alpha, normalized_difference, sorted(new_names.items()))
    

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



        # entropy calculation 
        m = G.number_of_edges()
        G_entropy_bitvector = 0
        n  = len(G.nodes())
        if m == 0:
            G_array_entropy = 0
        else:
            G_array_entropy = m * math.ceil(math.log2(n)) + n * math.ceil(math.log2(m))

        

        for v in G.nodes():
            degree = G.degree(v)
            if degree > 0:
                G_entropy_bitvector += degree * math.log2(m/degree)
        G_entropy_bitvector += math.log2(math.comb(m + n, n))





        reduced_entropy = 0
        m_dash = G_minus_T.number_of_edges()
        for v in G_minus_T.nodes():
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_entropy += indegree * math.log2(m_dash/indegree)
        
        reduced_entropy += 2* G_minus_T.number_of_nodes() + math.log2(math.comb(m_dash + G_minus_T.number_of_nodes(), G_minus_T.number_of_nodes()))

        # inserted extra -1 to assure that the tuple size always matches, no matter if we also calculate planar entropy
        entropy_tuple = [G_array_entropy, G_entropy_bitvector, reduced_entropy, -1]

        # calculating alpha 
        G_prime_density = density_greedy(G, 13)[0]
        G_density = G.number_of_edges() / G.number_of_nodes()
        alpha = G_prime_density / G_density


        # obviously not like real indegree, but 
        H_indegree = 0
        if m > 0:
            H_indegree = (entropy_tuple[1] - math.log2(math.comb(m+n,n)))/m

        upper_bound = entropy_tuple[1] - ((n)/(2 * alpha)) * H_indegree + (2* n)/math.log(2)

        normalized_difference = (upper_bound - entropy_tuple[2] )/ ( n * math.log2(n))
        

        # makes testing a lot easier
        if len(new_names) > 1000:
            new_names = {}

        return UndirectedTrexGraph(T, A_prime, S_prime, entropy_tuple, len(roots), alpha, normalized_difference, sorted(new_names.items()))
    

    def build_planar(self, G: nx.DiGraph):
        builder = Builder()
        G_built = builder.build(G)
        union_find = UnionFind()
        planar_edges = set()
        G_undirected = G.to_undirected()
        G_prime = G.copy()

        for u, v in G.edges():
            weight = G.in_degree(v)
            if G.has_edge(v, u):
                weight = min(G.in_degree(u), weight)
            G_undirected[u][v]['weight'] = weight

        # Finding all triangles 
        triangles = []
        for u in G_undirected.nodes():
            u_neighbors = set(G_undirected.neighbors(u))
            for v in u_neighbors:
                both_neighbors = u_neighbors.intersection(G_undirected.neighbors(v))
                for w in both_neighbors:
                    # making sure that there are no duplicates
                    if v<w<u:
                        triangle_weight = G_undirected[u][v]['weight'] + G_undirected[v][w]['weight'] + G_undirected[w][u]['weight']
                        triangles.append((triangle_weight, u, v, w))
        

        # the whole combining process, while adding the edges to the planar subgraph
        for (triangle_weight, u, v, w) in sorted(triangles):
            if union_find[u] != union_find[v] and union_find[v] != union_find[w] and union_find[u] != union_find[w]:

                if G_prime.has_edge(u,v) and not G_prime.has_edge(v,u):
                    planar_edges.add((u,v))
                    G_prime.remove_edge(u,v)
                elif G.has_edge(v,u) and not G.has_edge(u,v):
                    planar_edges.add((v,u))
                    G_prime.remove_edge(v,u)
                else:
                    if G.in_degree(u) > G.in_degree(v):
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
                    if G.in_degree(v) > G.in_degree(w):
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
                    if G.in_degree(w) > G.in_degree(u):
                        planar_edges.add((w,u))
                        G_prime.remove_edge(w,u)
                    else:
                        planar_edges.add((u,w))
                        G_prime.remove_edge(u,w)
                union_find.union(u,v)
                union_find.union(v,w)
                union_find.union(u,w)


        # adding remaining edges, that are not in triangles

        def weight_key(edge):
            return G_undirected[edge[0]][edge[1]]['weight']

        for u, v in sorted(G_undirected.edges(), key = weight_key):
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
                    if G.in_degree(u) > G.in_degree(v):
                        planar_edges.add((u,v))
                        G_prime.remove_edge(u,v)
                    else:
                        planar_edges.add((v,u))
                        G_prime.remove_edge(v,u)
                union_find.union(u,v)



        # entropy calculation
        reduced_entropy = 0
        m_dash = G_prime.number_of_edges()
        for v in G_prime.nodes():
            indegree = G_prime.in_degree(v)
            if indegree > 0:
                reduced_entropy += indegree * math.log2(m_dash/indegree)
        reduced_entropy += 4 * len(planar_edges) + math.log2(math.comb(m_dash + G_prime.number_of_nodes(), G_prime.number_of_nodes()))


        G_built.entropy_tuple[3] = reduced_entropy
    
        return G_built
