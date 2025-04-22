class Bits:
    
    def __init__(self, value, length=None):
        if type(value) is int:
            if value < 0:
                raise ValueError("Negative integer value")
            bin_str = bin(value)[2:]
            if length:
                bin_str = bin_str.zfill(length)
            self.bits = [bit == '1' for bit in bin_str]    
        elif type(value) is bytes:
            bit_str = ''.join(format(byte, '08b') for byte in value)
            self.bits = [bit == '1' for bit in bit_str]       
        else:  
            self.bits = [bool(b) for b in value]
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return Bits(self.bits[index])
        elif type(index) is int:
            if index < 0:
                index += len(self.bits)
            if index < 0 or index >= len(self.bits):
                raise IndexError("Index out of range")
        return self.bits[index]
    
    def __setitem__(self, index, value):
        self.bits[index] = bool(value)
    
    def parity_bit(self):   
        return sum(self.bits) % 2
    
    def __len__(self):
        return len(self.bits)
    
    def __str__(self):
        return ''.join(['1' if bit else '0' for bit in self.bits])
    
    def __repr__(self):
        return f"Bits({''.join(['1' if bit else '0' for bit in self.bits])})"
    
    def append(self, bit):
        self.bits.append(bool(bit))
    
    def pop(self, index=-1):
        return self.bits.pop(index)
    
    def __xor__(self, other):
        if len(self) != len(other):
            raise ValueError("Bit strings must be of the same length")
        return Bits([a ^ b for a, b in zip(self.bits, other.bits)])
    
    def __and__(self, other):
        if len(self) != len(other):
            raise ValueError("Bit strings must be of the same length")
        return Bits([a & b for a, b in zip(self.bits, other.bits)])
    
    def __add__(self, other):
        return Bits(self.bits + other.bits)
    
    def __mul__(self, scalar):
        if type(scalar) != int or scalar < 0:
            raise ValueError("Can only multiply by a non-negative integer")
        return Bits(self.bits * scalar)
    
    def __eq__(self, other):
        if type(other) is not Bits:
            raise ValueError("Can only compare with another Bits object")
        return self.bits == other.bits

    def to_bytes(self):
        pad_len = (8 - len(self.bits) % 8) % 8
        padded = [False] * pad_len + self.bits  # pad left for MSB-first
        return bytes(
            int(''.join(str(int(b)) for b in padded[i:i+8]), 2)
            for i in range(0, len(padded), 8)
        )
    
    def pad_left(self, length):
        if length < 0:
            raise ValueError("Length must be non-negative")
        self.bits = [False] * length + self.bits
        return self

    def pad_right(self, length):
        if length < 0:
            raise ValueError("Length must be non-negative")
        self.bits = self.bits + [False] * length
        return self
    
    def copy(self):
        return Bits(self.bits[:])
    
def polynomial_to_bits(degrees):
    """ input polnomial degress: {5, 3, 0}
        output bits: {1, 0, 1, 0, 0, 1} -> {p_1, ..., p_m-1, p_m}"""
    max_deg = max(degrees)
    bit_list = [1 if i in degrees else 0 for i in range(max_deg+1)]
    return Bits(bit_list)
    



