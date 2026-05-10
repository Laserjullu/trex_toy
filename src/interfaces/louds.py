from abc import ABC, abstractmethod

class AbstractLOUDS(ABC):

    @abstractmethod
    def parent(self, v: int) -> int:
        pass
        
    @abstractmethod
    def degree(self, v: int) -> int:
        pass
        
    @abstractmethod
    def child(self, v: int, i: int) -> int:
        pass
        
    @abstractmethod
    def child_rank(self, v: int, c: int) -> int:
        pass