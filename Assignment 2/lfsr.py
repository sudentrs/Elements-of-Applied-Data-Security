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

        self.output = None
        self.feedback = None


    def __iter__(self):
        return self

    def __next__(self):
        self.feedback = (self.poly_bits & self.state).parity_bit()
        self.output = self.state[-1]
        self.state = Bits([self.feedback] + self.state[:-1])
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
    P = Bits([1])              # P(x)
    Q = Bits([1])              # Q(x)
    m = 0
    r = 1

    for tau in range(N):
        # Compute discrepancy d
        d = 0
        for j in range(len(P)):
            if tau - j >= 0:
                d ^= P[j] & bits[tau - j]

        if d == 1:
            if 2 * m <= tau:
                R = Bits(P.bits[:])      # copy of P
                shifted_Q = Bits([0] * r + Q.bits)
                # Pad both to same length
                max_len = max(len(P), len(shifted_Q))
                P = Bits([0] * (max_len - len(P)) + P.bits)
                shifted_Q = Bits([0] * (max_len - len(shifted_Q)) + shifted_Q.bits)
                P = P ^ shifted_Q

                Q = R
                m = tau + 1 - m
                r = 0
            else:
                shifted_Q = Bits([0] * r + Q.bits)
                # Pad both to same length
                max_len = max(len(P), len(shifted_Q))
                P = Bits([0] * (max_len - len(P)) + P.bits)
                shifted_Q = Bits([0] * (max_len - len(shifted_Q)) + shifted_Q.bits)
                P = P ^ shifted_Q

        r += 1

    return P