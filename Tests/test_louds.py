from src.dummy.dummy_louds import DummyLouds, TreeNode
import unittest 
class test_louds(unittest.TestCase):
    def test_louds(self):
        root = TreeNode()
        root.children = [TreeNode(), TreeNode()]
    
        louds_tree = DummyLouds(root)
    
        assert louds_tree.degree(1) == 2
        assert louds_tree.degree(2) == 0

        assert louds_tree.child(1, 1) == 2
        assert louds_tree.child(1, 2) == 3
    
        assert louds_tree.parent(2) == 1
        assert louds_tree.parent(3) == 1
        assert louds_tree.child_rank(2) == 1
        assert louds_tree.child_rank(3) == 2
        print("Passed :)")

if __name__ == '__main__':
    unittest.main()

