from lfsr import LFSR
from bits import Bits

class AlternatingStep:
    def __init__(self, seed=None, polyC={5, 2, 0}, poly0={3, 1, 0}, poly1={4, 1, 0}):
        
        if seed is None:
            seed = [1] * (max(polyC) + max(poly0) + max(poly1))
            
        self.lfsrC = LFSR(polyC, state=Bits(seed[:max(polyC)]))
        self.lfsr0 = LFSR(poly0, state=Bits(seed[max(polyC):max(polyC) + max(poly0)]))
        self.lfsr1 = LFSR(poly1, state=Bits(seed[max(polyC) + max(poly0):max(polyC) + max(poly0) + max(poly1)]))  

        self.output = None

    def __iter__(self):
        return self

    def __next__(self):
        control_bit = next(self.lfsrC)
        
        if control_bit:
            bit1 = next(self.lfsr1)
            bit0 = self.lfsr0.output  # not clocked
        else:
            bit0 = next(self.lfsr0)
            bit1 = self.lfsr1.output # not clocked

        self.output = bit0 ^ bit1
        return self.output

    def run(self, N):
        """Returns the next N bits of the bit-generator (current output is not included)."""
        output_sequence = []
        for _ in range(N):
            output_sequence.append(next(self))
        return Bits(output_sequence)