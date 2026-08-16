from src.dummy.dummy_louds import DummyLouds
from src.dummy.dummy_wavelet import DummyWaveletTree
from src.dummy.dummy_bitvector import DummyBitvector



class DirectedTrexGraph:

    # new_names are only given if n < a certain threshhold (atm 1000)
    def __init__(self, T: DummyLouds, A_prime: DummyWaveletTree, S_prime: DummyBitvector, D: DummyBitvector,  new_names):
        self.T = T
        self.A_prime= A_prime
        self.S_prime = S_prime
        self.D = D
        self.new_names = new_names

    # for testing
    def print(self):
        if len(self.D.bits) < 100:
            print("T: " + str(self.T.B.bits))
            if self.A_prime.root is None:
                print("empty wavelet tree")
            elif self.A_prime.root.B is None:
                print("Wavelet TREE consits of only a single leaf with value " + str(self.A_prime.root.a))
            else:
                print("A_prime : some wavelet tree with root: " + str(self.A_prime.root.B.bits))
            print("S_prime': " + str(self.S_prime.bits))
            print("D: " + str(self.D.bits))
            print("Renamings: " + str(self.new_names))
    def outdegree(self,v: int) -> int:
        # how many zeros (out-edges) there are after our 1 to the next 1 
        outgoing_A_prime = self.S_prime.select(v + 1, 1) - self.S_prime.select(v,1) - 1
        outgoing_T = 0
        # we check if theres an edge pointing upwards
        if self.D.access(v - 1) == 0 and self.T.parent(v) != 0:
            outgoing_T +=1
        
        # we check how many edges point downwards to the children, meaning we count the ones in the interval of children within D
        if self.T.degree(v) != 0: 
            c_1 = self.T.child(v,1)
            c_k = self.T.child(v, self.T.degree(v))

            # typo in the paper, we defined D the other way around, such that 1 iff edge points downwards
            outgoing_T += self.D.rank(c_k - 1,1) - self.D.rank(c_1 - 2, 1)
        return outgoing_A_prime + outgoing_T
    
    def indegree(self, v: int) -> int:
        ingoing_A_prime = self.A_prime.rank(len(self.A_prime) -1, v)

        ingoing_T = 0

        if self.D.access(v-1) == 1 and self.T.parent(v) != 0:
            ingoing_T += 1
        
        if self.T.degree(v) != 0:
            c_1 = self.T.child(v,1)
            c_k = self.T.child(v, self.T.degree(v))
            ingoing_T += self.D.rank(c_k - 1, 0) - self.D.rank(c_1 - 2, 0)
        
        return ingoing_A_prime + ingoing_T
    
    def adjacent(self, u: int, v: int) -> bool:
        if self.T.parent(u) == v or self.T.parent(v) == u:
            return True
        
        # we simply check if the rank(v)/rank(u) changes within the outneighborhood of u/v within A_prime.
        # also small typo in the paper, should be v/u rather than 1 , also outdegree(u) is the wrong metric, need to use outdegree - T_outdegree
        A_prime_outdegree_u = self.S_prime.select(u + 1, 1) - self.S_prime.select(u, 1) - 1
        s = self.S_prime.select(u,1) - u
        if self.A_prime.rank(s + A_prime_outdegree_u, v) - self.A_prime.rank(s, v) >= 1:
            return True
        
        A_prime_outdegree_v = self.S_prime.select(v + 1, 1) - self.S_prime.select(v, 1) - 1 
        s_dash = self.S_prime.select(v,1) - v
        if self.A_prime.rank(s_dash + A_prime_outdegree_v, u) - self.A_prime.rank(s_dash, u) >= 1:
            return True
        return False 
    
    def outneighbor (self, v: int, i: int) -> int:
        if i > self.outdegree(v) or i < 1:
            print("there is no " + str(i) + "'th outneighbor of " + str(v))
            return -1

        # we calculate the outdegree of v in T by simply first checking the node to the parent and then count the number of children with a 1 in D
        T_outdegree = 0
        if self.D.access(v-1) == 0 and self.T.parent(v) != 0:
            T_outdegree += 1
        if self.T.degree(v) > 0:
            child_last = self.T.child(v, self.T.degree(v))
            child_first = self.T.child(v,1)
            T_outdegree += self.D.rank(child_last - 1, 1) - self.D.rank(child_first - 2 ,1)

        j = i
        # return parent in T if asked for 
        if i == 1 and self.D.access(v-1) == 0 and self.T.parent(v) != 0:
                return self.T.parent(v)
        # otherwise pick i-th or (i-1)-th outgoing child in T
        if i<= T_outdegree and self.T.degree(v) != 0:
            if self.D.access(v-1) == 0 and self.T.parent(v) != 0:
                j = i-1
            # first child
            c_1 = self.T.child(v,1)
            # number of ones that appear exclusively before the first child in d
            o = self.D.rank(c_1 - 2, 1)
            # we select the corect one in D to get the position of the i'th outchild and add 1 to make it a proper label again
            return self.D.select(j + o, 1) + 1
        
        # if it's not in T we look for it in A_prime by simply calculating the how manyth outneighbor it must be in A_prime
        # then by using S_prime we get the number of 0's before our edge, telling us where the outneighborhood begins in A_prime
        j = i - T_outdegree 
        s = self.S_prime.select(v, 1) - v
        return self.A_prime.access(s + j)
        

    def inneighbor(self, v:int, i: int) -> int:


        if i > self.indegree(v) or i< 1:
            print("there is no " + str(i) + "'th inneighbor of " + str(v))
            return -1
        
        has_ingoing_parent = (self.D.access(v-1) == 1 and self.T.parent(v) != 0)

        T_indegree = int(has_ingoing_parent)

        if self.T.degree(v) > 0:
            child_last = self.T.child(v, self.T.degree(v))
            child_first = self.T.child(v,1)
            T_indegree += self.D.rank(child_last - 1, 0) - self.D.rank(child_first - 2 ,0)
        j = i
        if i == 1 and has_ingoing_parent:
            return self.T.parent(v)
        if i<= T_indegree and self.T.degree(v) != 0:
            if has_ingoing_parent:
                j = i-1
            c_1 = self.T.child(v,1)
            o = self.D.rank(c_1 - 2, 0)
            return self.D.select(j + o, 0) + 1
        
        # rest was parallel to outneighbor, but here we now have to again calculate j, the how manyth inneihbor we are looking for in A_prime. Then we 
        # select the position of that edge in A_prime, then the belonging position in S_prime, and lastly we only need to calculate what node this belongs to in S_prime.

        j = i - T_indegree
        y = self.A_prime.select(j, v)
        a = self.S_prime.select(y + 1, 0)
        return self.S_prime.rank(a, 1) 
        
        
        
    
    def outneighbor_rank(self, v: int, w: int) -> int:

        # directed adjacency check
        if self.is_edge(v, w) == False:
            print("There's no edge from " + str(v) + " to " + str(w))
            return -1

        if self.T.parent(v) == w and self.D.access(v-1) == 0 and self.T.parent(v) != 0:
            return 1

        # if w is one of v's children
        if self.T.parent(w) == v and self.D.access(w-1) == 1:
            c_1 = self.T.child(v,1)
            j = self.D.rank(w - 1,1) - self.D.rank(c_1 - 2, 1)
            if self.D.access(v-1) == 0 and self.T.parent(v) != 0:
                j += 1
            return j

        T_outdegree = 0
        if self.D.access(v-1) == 0 and self.T.parent(v) != 0:
            T_outdegree += 1
        if self.T.degree(v) > 0:
            child_last = self.T.child(v, self.T.degree(v))
            child_first = self.T.child(v,1)
            T_outdegree += self.D.rank(child_last - 1, 1) - self.D.rank(child_first - 2 ,1)

        # s marks the start of v's outneighborhood in A_prime
        s = self.S_prime.select(v,1) - v
        # count how many times w already occurs in A_prime before v's outneighborhood begins
        r = self.A_prime.rank(s, w)
        # then we find the next occurrence of w and shift it by s again to get w's rank among v's outneighbors
        j = self.A_prime.select(r + 1 , w) - s
   
        return j + T_outdegree
    
    def inneighbor_rank(self, v: int, w: int) -> int:

        if self.is_edge(w, v) == False:
            print("There's no edge from " + str(w) + " to " + str(v))
            return -1

        if self.T.parent(v) == w and self.D.access(v-1) == 1 and self.T.parent(v) != 0:
            return 1
        
        if self.T.parent(w) == v and self.D.access(w-1) == 0:
            c_1 = self.T.child(v,1)
            j = self.D.rank(w - 1,0) - self.D.rank(c_1 - 2, 0)
            if self.D.access(v-1) == 1 and self.T.parent(v) != 0:
                j += 1
            return j
        
        T_indegree = 0
        if self.D.access(v-1) == 1 and self.T.parent(v) != 0:
            T_indegree += 1
        if self.T.degree(v) > 0:
            child_last = self.T.child(v, self.T.degree(v))
            child_first = self.T.child(v,1)
            T_indegree += self.D.rank(child_last - 1, 0) - self.D.rank(child_first - 2 ,0)

        # calculate where the outneighborhood of w starts within A_prime
        s = self.S_prime.select(w, 1) - w
        # j are the occurrences of w in A_prime up until (inclusive) (v -> w)
        j = self.A_prime.rank(s, v) + 1

        return j + T_indegree
    

    def is_edge(self, u: int, v: int) -> bool:
        
        # check in the Tree 
        if self.T.parent(u) == v and self.D.access(u - 1) == 0:
            return True
        if self.T.parent(v) == u and self.D.access(v - 1) == 1:
            return True
        
        # check in A_prime
        s = self.S_prime.select(u,1) - u
        A_prime_outdegree_u = self.S_prime.select(u + 1, 1) - self.S_prime.select(u, 1) - 1

        if self.A_prime.rank(s + A_prime_outdegree_u, v) - self.A_prime.rank(s, v) >= 1:
            return True
        return False

    

        
