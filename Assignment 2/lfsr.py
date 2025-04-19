from bits import Bits

def polynomial_to_bits(degrees):
    """ input polnomial degress: {5, 2, 0}
        output bits: {1, 0, 1, 0, 0, 1} -> {p_1, ..., p_m-1, p_m}"""
    max_deg = max(degrees)
    bit_list = [1 if i in degrees else 0 for i in range(max_deg+1)]
    return Bits(bit_list)

class LFSR:
    
    def __init__(self, poly, state=None):       
        self.poly = sorted(set(poly))
        self.length = max(self.poly)
        self.poly_bits = Bits(polynomial_to_bits(self.poly).bits[1:]) # ignore p_0

        if state is None:
            self.state = Bits([1] * self.length)
        elif isinstance(state, Bits):
            self.state = Bits(state.bits[:self.length])
        else:
            self.state = Bits(state, length=self.length)

        self.output = self.state[-1]
        self.feedback = None

    def __iter__(self):
        return self

    def __next__(self):
        self.feedback = (self.poly_bits & self.state).parity_bit()
        self.state = Bits([self.feedback] + self.state[:-1])
        self.output = self.state[-1]
        return self.output

    def run_steps(self, N=1, state=None):
        if state is not None:
            if type(state) is Bits:
                self.state = Bits(state.bits[:self.length])
            else:
                self.state = Bits(state, length=self.length)

        output_bits = []
        for i in range(N):
            output_bits.append(next(self))
        return Bits(output_bits)

    def cycle(self, state=None):
        if state is not None:
            if type(state) is Bits:
                self.state = Bits(state.bits[:self.length])
            else:
                self.state = Bits(state, length=self.length)

        initial_state = Bits(self.state.bits[:])
        output = [next(self)]
        while self.state != initial_state:
            output.append(next(self))
        return Bits(output)

    def __str__(self):
        return f"LFSR(state={str(self.state)}, poly={self.poly})"
    
    
def berlekamp_massey(bits):
    N = len(bits)
    P = Bits([1])              # feedback polynomial of LFSR -> leftmost bit is x^0
    Q = Bits([1])              # Q(x)
    m = 0                      # degree of P(x)
    r = 1                      

    for t in range(N):
        # Compute discrepancy d
        d = 0
        for i in range(len(P)):
            if t - i >= 0:
                d ^= P[i] & bits[t - i]

        if d == 1:
            if 2 * m <= t:
                R = P.copy()
                shifted_Q = Q.copy().pad_left(r)  # Left shift Q by r
                # equalize lengths
                max_len = max(len(P), len(shifted_Q))
                P = P.pad_right(max_len - len(P))
                shifted_Q = shifted_Q.pad_right(max_len - len(shifted_Q))
                P = P ^ shifted_Q
                Q = R
                m = t + 1 - m
                r = 0
            else:
                shifted_Q = Q.copy().pad_left(r)  # Left shift Q by r
                max_len = max(len(P), len(shifted_Q))
                P = P.pad_right(max_len - len(P))
                shifted_Q = shifted_Q.pad_right(max_len - len(shifted_Q))
                P = P ^ shifted_Q

        r += 1

    return {i for i, bit in enumerate(P) if bit}


