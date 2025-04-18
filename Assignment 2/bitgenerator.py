"""
from lfsr import LFSR
from bits import Bits

class AlternatingStep:
    def __init__(self, seed=None,
                 polyC={5, 2, 0}, poly0={3, 1, 0}, poly1={4, 1, 0}):

        # Default all bits to 1 if no seed is given
        if seed is None:
            self.lfsrC = LFSR(polyC)
            self.lfsr0 = LFSR(poly0)
            self.lfsr1 = LFSR(poly1)
        else:
            # Determine how many bits each LFSR needs
            lenC = max(polyC)
            len0 = max(poly0)
            len1 = max(poly1)

            # Ensure seed is a Bits object
            seed_bits = Bits(seed)
            total = lenC + len0 + len1

            # Pad seed if too short
            if len(seed_bits) < total:
                seed_bits = Bits([1] * total)

            sC = seed_bits[:lenC]
            s0 = seed_bits[lenC:lenC + len0]
            s1 = seed_bits[lenC + len0:lenC + len0 + len1]

            self.lfsrC = LFSR(polyC, state=sC)
            self.lfsr0 = LFSR(poly0, state=s0)
            self.lfsr1 = LFSR(poly1, state=s1)

        self.output = None
        
        next(self.lfsrC)
        next(self.lfsr0)
        next(self.lfsr1)

    def __iter__(self):
        return self

    def __next__(self):
        control_bit = next(self.lfsrC)

        if control_bit == 1:
            bit0 = next(self.lfsr0)
            bit1 = self.lfsr1.output  # not clocked
        else:
            bit0 = self.lfsr0.output  # not clocked
            bit1 = next(self.lfsr1)

        self.output = bit0 ^ bit1
        return self.output

    def run(self, op):
        output_sequence = []
        for _ in range(op):
            output_sequence.append(next(self))
        return output_sequence
        """

