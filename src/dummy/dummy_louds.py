import src.interfaces.louds as louds
from src.dummy.dummy_bitvector import DummyBitvector

# simple Tree Node, with children represented as a list
class TreeNode:
        def __init__(self):
            self.children = []


class DummyLouds(louds.AbstractLOUDS):

    # takes a the root of a tree (built with TreeNode) and builds the LOUDS Bitvector stored in self.B

    def __init__(self, roots: list[TreeNode]):
        # in case of a simple Tree with only one root
        if not isinstance(roots, list):
            roots = [roots]
            
        bits = [1] * len(roots)
        bits.append(0)
        current_level = roots
        while current_level:
            next_level = []
            for node in current_level:
                for child in node.children:
                    bits.append(1)
                    next_level.append(child)
                bits.append(0)
                
            current_level = next_level
        self.B = DummyBitvector(bits)

    # returns the unique parent of v: we first ask for the place where the node was first mentioned as a child
    # then check how many nodes were created before that, giving us the "name" of the parent
    def parent(self, v: int) -> int:
        return self.B.rank(self.B.select(v, 1), 0)
    
    # returns the number of children v has: we just check how many ones are between the end of the children of the node before and 
    # the end of v's children, we subtract one to cancel out the implicit difference of 1. 
    def degree(self, v:int) -> int: 
        return self.B.select(v+1,0) - self.B.select(v,0) - 1
    
    # returns the i'th child of v (1-based): we determine how many nodes were already created before v's first chiild and 
    # then just add i to get the name of the child. 
    def child(self, v: int, i: int) -> int:
        nodes_before = self.B.rank(self.B.select(v, 0), 1)
        # check if we are looking for a child, that does not exist, maybe mostly unecessary 
        #if self.B.rank(self.B.select(v,0), 1) - self.B.rank(self.B.select(v, 0) + i, 1) != 0:
        #    print(str(v) + " does not have " + str(i) + " children within the Tree")
        #    return -1
        return nodes_before + i

    # returns for what i, v is the i'th child of its parent (where parent is implicitly given): we simply determine the number 
    # of ones that are there up to the beginning of the begging of v's siblings and then subtract that from v, leavin us with the number of children that 
    # came before v + 1
    def child_rank(self, v: int) -> int:
        if v == 1:
            return 0
        prev_zero = self.B.predecessor(self.B.select(v, 1), 0)
        return v - self.B.rank(prev_zero, 1)
    
        
