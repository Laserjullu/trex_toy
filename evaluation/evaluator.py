
import networkx as nx 
import numpy as np
import math 
import time
from src.functions.density import density_greedy
from networkx.utils import UnionFind
from tqdm import tqdm

class Evaluator: 

    @staticmethod
    def evaluate(G, G_minus_T, G_built, G_greedy = None, planar = True):
        if isinstance(G, nx.DiGraph):
            type = "directed"
        elif isinstance(G, nx.Graph):
            type = "undirected"
        metrics = {"type": type, "n": G.number_of_nodes(), "m": G.number_of_edges()}
        metrics["avg cc"] = nx.average_clustering(G)

        if isinstance(G, nx.DiGraph):
            metrics.update(Evaluator.directed_metrics(G, G_minus_T))
            
        elif isinstance(G, nx.Graph):
            metrics.update(Evaluator.undirected_metrics(G, G_minus_T, G_greedy))
            
        if planar:
            planar_total, planar_edges = Evaluator.build_planar(G)
            metrics["total bits planar"] = planar_total
            metrics["planar edges"] = planar_edges
        return metrics

    @staticmethod 
    def undirected_metrics(G: nx.Graph, G_minus_T: nx.Graph, G_greedy: nx.DiGraph):
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
        
        trex_total = 0
        reduced_indegree_entropy = 0
        m_dash = G_minus_T.number_of_edges()
        for v in G_minus_T.nodes():
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_indegree_entropy += indegree * math.log2(m_dash/indegree)
        trex_entropy = reduced_indegree_entropy
        trex_total += reduced_indegree_entropy + 2* G_minus_T.number_of_nodes() + math.log2(math.comb(m_dash + G_minus_T.number_of_nodes(), G_minus_T.number_of_nodes()))

        entropy_tuple = [G_array_entropy, G_entropy_bitvector, G_entropy_bitvector_random, G_entropy_bitvector_greedy, trex_total, -1]

        start = time.time()

        iterations = 1
        if G.number_of_edges() < 1000000:
            iterations = 13
        G_prime_density = density_greedy(G, iterations)[0]

        G_density = G.number_of_edges() / G.number_of_nodes()
        alpha_16 = G_prime_density / G_density
        print("Greedy took: " + str(time.time() - start))

        H_indegree = 0
        if m > 0: 
            # we take the the greedy approach to compare with the bound 
            H_indegree = (entropy_tuple[3] - math.log2(math.comb(m+n, n)))/m

        H_indegree_total = H_indegree * m 
        upper_bound_16 = H_indegree_total - ((n)/(2 * alpha_16)) * H_indegree + (2* n)/math.log(2)

        non_zero_indegrees = 0
        for v in G_greedy.nodes():
            if G_greedy.in_degree(v) > 0:
                non_zero_indegrees += 1
        
        alpha_17 = n/non_zero_indegrees
        upper_bound_17 = H_indegree_total - ((n)/(2 * alpha_17)) * H_indegree + (2* n)/math.log(2)

        indegrees = []
        for v in G_greedy.nodes():
            indegrees.append(G_greedy.in_degree(v))
        indegree_CV = np.var(indegrees)/np.mean(indegrees)

        twin_classes = {}
        maximum_class_degree = 0
        for v in G.nodes():
            neighbors = tuple(sorted(G.neighbors(v)))
            if neighbors not in twin_classes: 
                twin_classes[neighbors] = []
                twin_classes[neighbors].append(v)
            else:
                maximum_class_degree = max(maximum_class_degree, len(neighbors))
        num_classes = len(twin_classes)

        return{
            "array total bits": G_array_entropy,
            "bitvector total bits": G_entropy_bitvector,
            "bitvector random total bits": G_entropy_bitvector_random, 
            "bitvector greedy total bits": G_entropy_bitvector_greedy,
            "total bits trex": trex_total, 
            "trex entropy": trex_entropy,
            "alpha 1.6": alpha_16,
            "upper bound 1.6": upper_bound_16,
            "non zero indegree nodes": non_zero_indegrees,
            "upper bound 1.7": upper_bound_17,
            "indegree coefficient of variation": indegree_CV,
            "number of classes": num_classes,
            "maximum class degree": maximum_class_degree
        }


    @staticmethod
    def directed_metrics(G: nx.DiGraph, G_minus_T: nx.DiGraph):

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





        trex_total = 0
        reduced_indegree_entropy = 0
        m_dash = G_minus_T.number_of_edges()
        for v in tqdm(G_minus_T.nodes(), total = len(G_minus_T.nodes())):
            indegree = G_minus_T.in_degree(v)
            if indegree > 0:
                reduced_indegree_entropy += indegree * math.log2(m_dash/indegree)
        trex_entropy = reduced_indegree_entropy
        trex_total += reduced_indegree_entropy + 3* G_minus_T.number_of_nodes() + math.log2(math.comb(m_dash + G_minus_T.number_of_nodes(), G_minus_T.number_of_nodes()))

        # extra zero in case planar is added later on. 
        entropy_tuple = [G_array_entropy, G_entropy_bitvector, trex_total, -1]

        start = time.time()
        # calculating alpha 
        G_multigraph = nx.MultiGraph()
        # need to manually add the edges, otherwise only one direction is added. 
        G_multigraph.add_edges_from(G.edges)
        G_multigraph.add_nodes_from(G.nodes)
        
        # choosing 13 Iterations, because in Boob et al's Paper it took 12.69 iterations to reach the optimum on avg. 
        print("beginning of Greedy alpha determination: ")
        start = time.time()
        iterations = 1
        if G.number_of_edges() < 1000000:
            iterations = 13
        G_prime_density = density_greedy(G_multigraph, iterations)[0]
        del G_multigraph

        G_density = G.number_of_edges() / G.number_of_nodes()
        alpha_16 = G_prime_density / G_density
        print("Greedy took: " + str(time.time() - start))



        H_indegree = 0
        if m > 0:
            H_indegree = (entropy_tuple[1] - math.log2(math.comb(m+n,n)))/m
        

        H_indegree_total = H_indegree * m 
        upper_bound_16 = H_indegree_total - ((n)/(2 * alpha_16)) * H_indegree + (2* n)/math.log(2)

        non_zero_indegrees = 0
        for v in G.nodes():
            if G.in_degree(v) > 0:
                non_zero_indegrees += 1
        
        alpha_17 = n /non_zero_indegrees
        upper_bound_17 = H_indegree_total - ((n)/(2 * alpha_17)) * H_indegree + (2* n)/math.log(2)

        indegrees = []
        for v in G.nodes(): 
            indegrees.append(G.in_degree(v))
        indegree_CV = np.var(indegrees)/np.mean(indegrees)

        # number of theoretical twin classes 
        twin_classes = {}
        maximum_class_degree = 0
        for v in G.nodes():
            in_neighbors = tuple(sorted(G.predecessors(v)))
            out_neighbors = tuple(sorted(G.successors(v)))
            neighbors = (in_neighbors, out_neighbors)
            if neighbors not in twin_classes:
                twin_classes[neighbors] = []
                twin_classes[neighbors].append(v)
            else:
                maximum_class_degree = max(maximum_class_degree, len(in_neighbors) + len(out_neighbors))
                twin_classes[neighbors].append(v)
            

        num_classes = len(twin_classes)
        


        return{
            "array total bits": G_array_entropy,
            "bitvector total bits": G_entropy_bitvector,
            "bitvector random total bits": -1, 
            "bitvector greedy total bits": -1,
            "total bits trex": trex_total, 
            "trex entropy": trex_entropy,
            "alpha 1.6": alpha_16,
            "upper bound 1.6": upper_bound_16,
            "non zero indegree nodes": non_zero_indegrees,
            "upper bound 1.7": upper_bound_17,
            "indegree coefficient of variation": indegree_CV,
            "number of classes": num_classes,
            "maximum class degree": maximum_class_degree
        }

    @staticmethod
    def build_planar(G):
        if isinstance(G, nx.DiGraph):   
            G_undirected = G.to_undirected()

            for u, v in G.edges():
                weight = G.in_degree(v)
                if G.has_edge(v, u):
                    weight = min(G.in_degree(u), weight)
                G_undirected[u][v]['weight'] = weight
            
            planar_edges, G_prime = Evaluator.extract_planar_edges(G_undirected, G.copy(), G)
            
            planar_total = 0
            m_dash = G_prime.number_of_edges()
            for v in G_prime.nodes():
                indegree = G_prime.in_degree(v)
                if indegree > 0:
                    planar_total += indegree * math.log2(m_dash/indegree)
            planar_total += 2.092 * G.number_of_nodes() + len(planar_edges) + math.log2(math.comb(m_dash + G_prime.number_of_nodes(), G_prime.number_of_nodes()))

        
            return planar_total, len(planar_edges)

        elif isinstance(G, nx.Graph):
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
            planar_edges, G_prime = Evaluator.extract_planar_edges(G_undirected, G_prime)

    

            planar_total = 0
            m_dash = G_prime.number_of_edges()
            for v in G_prime.nodes():
                indegree = G_prime.in_degree(v)
                if indegree > 0:
                    planar_total += indegree * math.log2(m_dash/indegree)
            # 2.5 because we leave out the edges for the direction bitvector.
            planar_total += 2.092 * G.number_of_nodes() + math.log2(math.comb(m_dash + G_prime.number_of_nodes(), G_prime.number_of_nodes()))

            return planar_total, len(planar_edges)

    @staticmethod
    def extract_planar_edges(G_undirected: nx.Graph, G_prime: nx.DiGraph, G_original: nx.DiGraph = None):
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

            
