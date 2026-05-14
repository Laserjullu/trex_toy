from src.interfaces.wavelet import AbstractWaveletTree
from src.dummy.dummy_bitvector import DummyBitvector

# simple wavelet node, where we store the interval of the letters included, the bitvector as well as the children. 
class Wavelet_Node:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b
        self.B = None
        self.l = None
        self.r = None

class DummyWaveletTree(AbstractWaveletTree):
   
    def __init__(self, alphabet: list[int]):
        self.length = len(alphabet)
        # protection against empty A_prime, if G is already a spanning tree
        if self.length == 0:
            self.root = None
        else:
            # expects a sequence of integers
            self.root = self.build(alphabet, min(alphabet), max(alphabet))
        
    
    # adds log(m - n + 1) bits, but we dont have to call len(self.root.B.bits) anymore. 
    def __len__(self) -> int:
        return self.length

    def build(self, arr: list[int], a: int, b: int) -> Wavelet_Node:

        node = Wavelet_Node(a, b)
        if a == b:
            return node

        mid = (a + b) // 2
        bits = []
        left_arr = []
        right_arr = []

        for x in arr:
            if x <= mid:
                bits.append(0)
                left_arr.append(x)
            else:
                bits.append(1)
                right_arr.append(x)

    
        node.B = DummyBitvector(bits)
        
        node.l = self.build(left_arr, a, mid)
        node.r = self.build(right_arr, mid + 1, b)
        
        return node

    def access(self, i: int) -> int:

        if self.root is None: 
            print("Empty wavelet tree, shouldn't access")
            return -1

        node = self.root

        while node.a != node.b:
    
            if node.B.access(i) == 0:
                i = node.B.rank(i, 0) - 1 
                node = node.l
            else:
                i = node.B.rank(i, 1) - 1
                node = node.r
        return node.a

    def rank(self, i: int, letter: int) -> int:
        if self.root is None:
            return 0

        # in the indegree as well as the outdegree calculation it checks the rank of a letter that is not 
        # in A' anymore, therefore we need this check 
        if letter < self.root.a or letter > self.root.b:
            return 0

        node = self.root
        while node.a != node.b:

            if letter <= (node.a + node.b) // 2:
                # i = -1 case is handled by empty list in B.rank
                i = node.B.rank(i, 0) - 1
                node = node.l
            else:
                # as always -1 because of zero based indexing, but rank's output is a one based count
                i = node.B.rank(i, 1) - 1   
                node = node.r
        return i + 1
        


    def select(self, j: int, letter: int) -> int:
        if self.root is None:
            print("Empty wavelet tree, there is no " + str(j) + "'th occurrence of " + str(letter))

        curr = self.root
        nodes = []
        directions = []

        while curr.a != curr.b:

        # didn't really find navarros way intuitive, so I do a traversal to the correct bit in the leaf, where we remember the path, so we can reconstruct the position in the root's bitvector. 

            if letter <= (curr.a + curr.b) // 2:
                nodes.append(curr)
                directions.append(0)
                curr = curr.l
            else:
                nodes.append(curr)
                directions.append(1)
                curr = curr.r
        result = j - 1

        # reconstruction of the position. 
        while nodes:
            node = nodes.pop()
            bit = directions.pop()
            result = node.B.select(result + 1 , bit)
        return result