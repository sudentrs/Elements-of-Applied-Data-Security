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

from bits import Bits
from lfsr import LFSR

class AlternatingStep:
    def __init__(self, seed=None, polyC=None, poly0=None, poly1=None):
        """
        Initialize the Alternating-Step Generator.
        
        Args:
            seed: Optional seed to initialize all three LFSRs (first bits for C, then 0, then 1)
            polyC: Polynomial for control LFSR (default x^5 + x^2 + 1)
            poly0: Polynomial for first data LFSR (default x^3 + x + 1)
            poly1: Polynomial for second data LFSR (default x^4 + x + 1)
        """
        # Set default polynomials if not provided
        if polyC is None:
            polyC = {5, 2, 0}  # x^5 + x^2 + 1
        if poly0 is None:
            poly0 = {3, 1, 0}  # x^3 + x + 1
        if poly1 is None:
            poly1 = {4, 1, 0}  # x^4 + x + 1

        # Initialize states from seed if provided
        if seed is not None:
            if isinstance(seed, Bits):
                seed_bits = seed.bits.copy()
            else:
                seed_bits = Bits(seed).bits.copy()
            
            # Split seed into parts for each LFSR
            len_C = max(polyC)
            len_0 = max(poly0)
            len_1 = max(poly1)
            
            # Get bits for each LFSR (C first, then 0, then 1)
            bits_C = seed_bits[:len_C]
            bits_0 = seed_bits[len_C:len_C+len_0]
            bits_1 = seed_bits[len_C+len_0:len_C+len_0+len_1]
            
            # Pad with 1s if seed was too short
            bits_C += [True] * (len_C - len(bits_C))
            bits_0 += [True] * (len_0 - len(bits_0))
            bits_1 += [True] * (len_1 - len(bits_1))
            
            self.lfsrC = LFSR(polyC, Bits(bits_C[:len_C]))
            self.lfsr0 = LFSR(poly0, Bits(bits_0[:len_0]))
            self.lfsr1 = LFSR(poly1, Bits(bits_1[:len_1]))
        else:
            # Initialize all LFSRs with all 1s
            self.lfsrC = LFSR(polyC)
            self.lfsr0 = LFSR(poly0)
            self.lfsr1 = LFSR(poly1)
        
        self.output = None

    def __iter__(self):
        return self

    def __next__(self):
        # Get control bit
        control_bit = next(self.lfsrC)

        # Clock LFSR0 if control_bit is 1, else clock LFSR1
        if control_bit:
            bit0 = next(self.lfsr0)
            bit1 = self.lfsr1.state[-1]  # Current output without clocking
        else:
            bit1 = next(self.lfsr1)
            bit0 = self.lfsr0.state[-1]  # Current output without clocking

        # Output is XOR of both LFSRs' current outputs
        self.output = bit0 ^ bit1
        return self.output

    def run_steps(self, N=1):
        """Run N steps of the generator and return the output bits"""
        output_bits = []
        for _ in range(N):
            output_bits.append(next(self))
        return Bits(output_bits)

    def __str__(self):
        return (f"AlternatingStepGenerator(\n"
                f"  Control: {str(self.lfsrC)}\n"
                f"  Data0: {str(self.lfsr0)}\n"
                f"  Data1: {str(self.lfsr1)}\n"
                f")")