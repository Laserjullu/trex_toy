import unittest
from src.dummy.dummy_bitvector import DummyBitvector

class test_bitvector(unittest.TestCase):


    def test_bitvector(self):
        B = DummyBitvector([1, 0, 1, 1, 0, 1])
    
        assert B.rank(2, 1) == 2 
        assert B.rank(4, 0) == 2  
    
        assert B.select(1, 1) == 0 
        assert B.select(2, 0) == 4
    
        assert B.predecessor(3, 1) == 3 
        assert B.predecessor(4, 0) == 4
    
        assert B.successor(2, 1) == 3 
        assert B.successor(4, 1) == 5

if __name__ == '__main__':
    unittest.main()