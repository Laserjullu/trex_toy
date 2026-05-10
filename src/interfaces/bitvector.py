from abc import ABC, abstractmethod

class AbstractBitVector(ABC):
    
    @abstractmethod
    def access(self, i: int) -> int:
        pass
        
    @abstractmethod
    def rank(self, i: int, bit: int = 1) -> int:
        pass
        
    @abstractmethod
    def select(self, j: int, bit: int = 1) -> int:
        pass
    @abstractmethod
    def predecessor(self, i: int, bit: int = 1) -> int:
        pass
    @abstractmethod
    def successor(self, i: int, bit: int = 1) -> int:
        pass
    
