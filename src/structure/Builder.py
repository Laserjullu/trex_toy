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
import random


class Builder:

    def __init__(self):
        pass


    def build(self, G, planar: bool = False):
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
                #weight = min(G.in_degree(u), weight)
                #temporal
                weight = max(G.in_degree(u), weight)
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
            #Tree = nx.minimum_spanning_tree(subgraph)
            Tree = nx.maximum_spanning_tree(subgraph)
            #temporary
            #Tree = self.random_spanning_tree(subgraph)
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
                

                if G.has_edge(parent, child) and G.has_edge(child, parent):
                    # if G.in_degree(child) <= G.in_degree(parent):
                    #     D[i-1] = 1
                    #     G_minus_T.remove_edge(parent, child)
                    # else:
                    #     G_minus_T.remove_edge(child,parent)
                    #temporal
                     if G.in_degree(child) > G.in_degree(parent):
                         D[i-1] = 1
                         G_minus_T.remove_edge(parent, child)
                     else:
                         G_minus_T.remove_edge(child,parent)
                    # if random.random() < 0.5:
                    #     D[i-1] = 1
                    #     G_minus_T.remove_edge(parent, child)
                    # else:
                    #     G_minus_T.remove_edge(child,parent)
                elif G.has_edge(parent, child):
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

        # makes testing a lot easier
        if len(new_names) > 1000:
            new_names = {}

        return DirectedTrexGraph(T, A_prime, S_prime, D, len(roots), sorted(new_names.items())), G_minus_T
    

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
            #Tree = nx.minimum_spanning_tree(subgraph)
            #temporary
            Tree = nx.maximum_spanning_tree(subgraph)
            #Tree = self.random_spanning_tree(subgraph)
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

        
        return UndirectedTrexGraph(T, A_prime, S_prime, len(roots), sorted(new_names.items())), G_minus_T, G_greedy
    
    def random_spanning_tree(self, G: nx.Graph) -> nx.Graph:
        for (u,v) in G.edges():
            G[u][v]['weight'] = random.random()
        return nx.minimum_spanning_tree(G)