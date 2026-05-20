import networkx as nx
from src.dummy.dummy_louds import DummyLouds, TreeNode
from src.dummy.dummy_wavelet import DummyWaveletTree
from src.dummy.dummy_bitvector import DummyBitvector



class UndirectedTrexGraph:

    def __init__(self, T: DummyLouds, A_prime: DummyWaveletTree, S_prime: DummyBitvector, entropy_tuple, num_of_trees: int, alpha: float, new_names: map = {}):
        self.T = T
        self.A_prime= A_prime
        self.S_prime = S_prime
        self.new_names = new_names
        self.num_of_trees = num_of_trees
        self.entropy_tuple = entropy_tuple
        self.alpha = alpha

    # for testing
    def print(self):
        if len(self.A_prime) < 100:
            print("T: " + str(self.T.B.bits))
            print("A_prime : some wavelet tree with root: " + str(self.A_prime.root.B.bits))
            print("S_prime': " + str(self.S_prime.bits))
            print("Renamings: " + str(self.new_names))
        print("Array based: " + str(self.entropy_tuple[0]) + ", Entropy with Wavelet Tree plus S but non reduced: " + str(self.entropy_tuple[1]) + ", Reduced: " + str(self.entropy_tuple[2]))
        print("alpha: " + str(self.alpha))
    
    def degree(self, v: int) -> int:
        T_degree = self.T.degree(v)
        if v > self.num_of_trees:
            T_degree += 1
        s = self.S_prime.select(v, 1)
        s_dash = self.S_prime.select(v + 1,1)
        A_prime_outdegree = s_dash - s - 1
        A_prime_indegree = self.A_prime.rank(len(self.A_prime) - 1, v)
        return T_degree + A_prime_outdegree + A_prime_indegree
    
    def adjacent(self, u: int, v: int) -> bool:
        if self.T.parent(u) == v or self.T.parent(v) == u:
            return True
        
        # we simply check if the rank(v/u) changes within the outneighborhood of u/v in A_prime.
        # also small typo in the paper, should be v/u rather than 1 , also outdegree(u) is the wrong metric, need to use outdegree - T_outdegree
        A_prime_outdegree_u = self.S_prime.select(u + 1, 1) - self.S_prime.select(u, 1) - 1
        s = self.S_prime.select(u,1) - u + 1
        if self.A_prime.rank(s + A_prime_outdegree_u -1, v) - self.A_prime.rank(s - 1, v) >= 1:
            return True
        A_prime_outdegree_v = self.S_prime.select(v + 1, 1) - self.S_prime.select(v, 1) - 1 
        s_dash = self.S_prime.select(v,1) - v + 1
        if self.A_prime.rank(s_dash + A_prime_outdegree_v - 1, u) - self.A_prime.rank(s_dash - 1, u) >= 1:
            return True
        return False 
    
    # first tree neighbors, then A_prime "outneighbors", then A_prime "inneighbors"
    def neighbor(self, v: int, i: int) -> int: 
        j = i
        T_degree = self.T.degree(v)

        # check whether we are simply asking for the parent 
        if i == 1 and v > self.num_of_trees:
            return self.T.parent(v)

        # increase the degree if v has a parent within the tree, decrease the neighbor id we are looking for by one
        if v > self.num_of_trees:
            j -= 1
            T_degree += 1
        # now we look within the Tree neighbors
        if i <= T_degree:
            return self.T.child(v,j)
        
        # checking "outneighbors" in A_prime
        remaining = i - T_degree
        s = self.S_prime.select(v, 1)
        s_dash = self.S_prime.select(v+1, 1)
        A_prime_outdeg = s_dash - s - 1

        if remaining <= A_prime_outdeg:
            A_prime_pos = s - v + 1
            return self.A_prime.access(A_prime_pos + remaining - 1)
        
        # checking "inneighbors" in A_prime
        remaining -= A_prime_outdeg 
        if remaining <= self.A_prime.rank(len(self.A_prime) - 1, v):
            # position in A_prime where the
            pos_A = self.A_prime.select(remaining, v)
            # position in S_prime where this edge is declared
            pos_S = self.S_prime.select(pos_A+1, 0)
            # finally the vetice, to which this edge belongs
            return self.S_prime.rank(pos_S, 1)
        
        print(str(v) + " has no " + str(i) + "'th neighbor")
        return -1
        
    # this unfortunately isn't symmetric, but shoult it be? Do I even have to implement it? 
    def neighbor_rank(self, v: int, w: int) -> int:
    
        if self.adjacent(v, w) == False:
            print(str(v) + " and " + str(w) + " are no neighbors")
            return -1
        
        # checking if w is v's parent and adjusting T_degree
        T_degree = self.T.degree(v)
        if v > self.num_of_trees:
            T_degree += 1
            if self.T.parent(v) == w:
                return 1
        
        # checking if w is one of v's children
        if self.T.parent(w) == v:
            T_rank = self.T.child_rank(w)
            if v > self.num_of_trees:
                T_rank += 1
            return T_rank
        
        s = self.S_prime.select(v, 1)
        s_dash = self.S_prime.select(v + 1, 1)
        A_prime_outdegree = s_dash - s - 1
        A_prime_pos = s - v + 1
        
        # check if w is an outneighbor in A_prime
        if self.A_prime.rank(A_prime_pos - 1, w) != self.A_prime.rank(A_prime_pos + A_prime_outdegree - 1, w):
            # the posision of the edge v -> w in A_prime
            pos = self.A_prime.select(self.A_prime.rank(A_prime_pos - 1, w) + 1, w)
            # 1 to account for the zero based indexing the difference of the two positions 
            difference = pos - A_prime_pos + 1
            return difference + T_degree
        
        # now w must be within the inneighbors of v
        pos_A_prime = self.S_prime.select(w + 1, 1) -  w
        num_of_occ = self.A_prime.rank(pos_A_prime - 1, v)
        return T_degree + A_prime_outdegree + num_of_occ

        
    def entropy (self) -> tuple[float, float, float]:
        return self.entropy_tuple
    
    

        
