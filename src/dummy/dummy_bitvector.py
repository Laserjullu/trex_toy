from src.interfaces.bitvector import AbstractBitVector


# zero based, because it turned out to sometimes be more intuitive
# queries default to v = 1, if bit omitted
class DummyBitvector(AbstractBitVector):

    #could also store the length
    def __init__(self, bits: list[int]):
        self.bits = bits

    def access(self, i: int) -> int:
        return self.bits[i]

    def rank(self, i: int, bit: int = 1) -> int:
        return self.bits[:i + 1].count(bit)

    def select(self, j: int, bit: int = 1) -> int:
        count = 0

        for i in range(len(self.bits)):
            if self.access(i) == bit:
                count += 1
                if count == j:
                    return i
        i += 1
        print("there are fewer than " + str(j) + " occurences of bit " + str(bit))
    
    # inklusive predecessor, exklusive sucessor
    def predecessor(self, i: int, bit: int = 1) -> int:
        return self.select(self.rank(i, bit), bit)
    
    def successor(self, i: int, bit: int = 1) -> int:
        return self.select(self.rank(i,bit) + 1, bit)
    