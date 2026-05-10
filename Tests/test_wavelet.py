from src.dummy.dummy_wavelet import DummyWaveletTree
import unittest

class test_wavelet(unittest.TestCase):

    def test_wavelet(self):
        wt = DummyWaveletTree([3, 1, 2, 4, 1, 3])
    
        assert wt.access(1) == 1
        assert wt.access(5) == 3
    
        assert wt.rank(5, 3) == 2 
        assert wt.rank(0, 1) == 0
    
        assert wt.select(1, 3) == 0 
        assert wt.select(2, 3) == 5 

if __name__ == '__main__':
    unittest.main()
