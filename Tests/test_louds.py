from src.dummy.dummy_louds import DummyLouds, TreeNode
import unittest 
class test_louds(unittest.TestCase):
    def test_louds(self):
        root = TreeNode()
        root.children = [TreeNode(), TreeNode()]
    
        louds_tree = DummyLouds(root)
    
        self.assertEqual(louds_tree.degree(1), 2)
        self.assertEqual(louds_tree.degree(2), 0)

        self.assertEqual(louds_tree.child(1, 1), 2)
        self.assertEqual(louds_tree.child(1, 2), 3)
    
        self.assertEqual(louds_tree.parent(2), 1)
        self.assertEqual(louds_tree.parent(3), 1)
        self.assertEqual(louds_tree.child_rank(2), 1)
        self.assertEqual(louds_tree.child_rank(3), 2)

if __name__ == '__main__':
    unittest.main()

