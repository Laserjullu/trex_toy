from abc import ABC, abstractmethod
from typing import Any

class AbstractWaveletTree(ABC):
    
    @abstractmethod
    def access(self, i: int) -> int:
        pass
        
    @abstractmethod
    def rank(self, i: int, symbol: int) -> int:
        pass
        
    @abstractmethod
    def select(self, j: int, symbol: int) -> int:
        pass