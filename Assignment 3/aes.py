class AES:
    def __init__(self, key):
        self.key = key

    def encrypt(self, plaintext):
        if len(plaintext) != 16:
            raise ValueError("Plaintext must be 16 bytes long")
        Nr = {16: 10, 24: 12, 32: 14}[len(self.key)]
        
        round_keys = self.key_expansion()
        state = self.to_matrix(plaintext)
        state = self.add_round_key(state, round_keys[0]) #k_0
        for i in range(1, Nr):
            state = self.round(state, round_keys[i])
        state = self.final_round(state, round_keys[Nr])
        return self.to_bytes(state)
    
    @staticmethod
    def add_round_key(state, round_key):
        for s_row, key_row in zip(state, round_key):
            for i in range(len(s_row)):
                s_row[i] ^= key_row[i]          
        return state    
        
        """return [[s ^ rk for s, rk in zip(state_row, key_row)]
                for state_row, key_row in zip(state, round_key)]"""
                
    @staticmethod
    def byte_substitution(state):
        for row in state:
            for i in range(len(row)):
                row[i] = AES.s_box[row[i]]
        return state
        """return [[AES.s_box[b] for b in row] for row in state]"""
        
    @staticmethod
    def shift_rows(state):
        return [
            state[0],
            state[1][1:] + state[1][:1],
            state[2][2:] + state[2][:2],
            state[3][3:] + state[3][:3],
        ]
        
    @staticmethod
    def mix_column(state):
        new_state = state
        for i in range(4):
            col = [state[j][i] for j in range(4)]
            mixed_col = AES.mix_single_column(col)
            for j in range(4):
                new_state[j][i] = mixed_col[j]
        return new_state
    
    @staticmethod
    def mix_single_column(col):
        a0, a1, a2, a3 = col
        r0 = AES.mul_by_02(a0) ^ AES.mul_by_03(a1) ^ a2 ^ a3
        r1 = a0 ^ AES.mul_by_02(a1) ^ AES.mul_by_03(a2) ^ a3
        r2 = a0 ^ a1 ^ AES.mul_by_02(a2) ^ AES.mul_by_03(a3)
        r3 = AES.mul_by_03(a0) ^ a1 ^ a2 ^ AES.mul_by_02(a3)
        return [r0, r1, r2, r3]
    
    @staticmethod
    def mul_by_02(a):
        if a & 0x80:
            return ((a << 1) ^ 0x1B) & 0xFF
        else:
            return (a << 1) & 0xFF

    @staticmethod
    def mul_by_03(a):
        return AES.mul_by_02(a) ^ a
    
    def key_expansion(self):
        key_bytes = list(self.key)
        Nk = len(key_bytes) // 4  # number of words in the original key
        Nr = {16: 10, 24: 12, 32: 14}[len(self.key)] # number of rounds
        Nb = 4  # number of words in the state

        RC = AES.generate_rcoef(Nr)
        key_schedule = [key_bytes[i:(i+4)] for i in range(0, len(key_bytes), 4)] # 4 bytes = 1 word
        i = Nk 

        while len(key_schedule) < Nb * (Nr + 1):
            temp = key_schedule[-1]
            if i % Nk == 0:
                temp = AES.g(temp, RC[i // Nk - 1])
            elif Nk == 8 and i % Nk == 4:
                temp = [AES.s_box[b] for b in temp]
                
            word = [a ^ b for a, b in zip(key_schedule[i - Nk], temp)]
            key_schedule.append(word)
            i += 1

        round_keys = []
        for i in range(0, len(key_schedule), 4):
            words = key_schedule[i:i + 4]
            matrix = [[words[col][row] for col in range(4)] for row in range(4)]
            round_keys.append(matrix)
        return round_keys

    @staticmethod
    def generate_rcoef(rounds_needed):
        rcon = []
        c = 1
        for _ in range(rounds_needed):
            rcon.append(c)
            c = AES.mul_by_02(c)
        return rcon

    @staticmethod
    def g(word, rc_i):
        word = word[1:] + word[:1]
        word = [AES.s_box[i] for i in word]
        word[0] ^= rc_i
        return word
    
    @staticmethod
    def round(state, round_key):
        state = AES.byte_substitution(state)
        state = AES.shift_rows(state)
        state = AES.mix_column(state)
        state = AES.add_round_key(state, round_key)
        return state

    @staticmethod
    def final_round(state, round_key):
        state = AES.byte_substitution(state)
        state = AES.shift_rows(state)
        state = AES.add_round_key(state, round_key)
        return state
    
    @staticmethod
    def to_matrix(input_bytes):
        return [list(input_bytes[i::4]) for i in range(4)]

    @staticmethod
    def to_bytes(matrix):
        return bytes([matrix[row][col] for col in range(4) for row in range(4)])
  
    s_box = [
        0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
        0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
        0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
        0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
        0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc,
        0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
        0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a,
        0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
        0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
        0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
        0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
        0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
        0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85,
        0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
        0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
        0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
        0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17,
        0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
        0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88,
        0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
        0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
        0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
        0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9,
        0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
        0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6,
        0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
        0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
        0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
        0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94,
        0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
        0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68,
        0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
    ]

    def partially_encrypt(self, plaintext, num_round=None):
        if len(plaintext) != 16:
            raise ValueError("Plaintext must be 16 bytes long")

        default_rounds = {16: 10, 24: 12, 32: 14}[len(self.key)]
        if num_round is None or num_round >= default_rounds:
            #num_round = default_rounds
            return self.encrypt(plaintext)

        round_keys = self.key_expansion()
        state = self.to_matrix(plaintext)
        state = self.add_round_key(state, round_keys[0])

        for i in range(1, num_round+1):
            state = self.round(state, round_keys[i])

        #if num_round == default_rounds:                                #maybe remove this
            #state = self.final_round(state, round_keys[num_round])

        return self.to_bytes(state)
    
    def decrypt(self, ciphertext):
        if len(ciphertext) != 16:
            raise ValueError("Ciphertext must be 16 bytes long")

        Nr = {16: 10, 24: 12, 32: 14}[len(self.key)]
        round_keys = self.key_expansion()

        state = self.to_matrix(ciphertext)
        state = self.add_round_key(state, round_keys[Nr])

        for i in range(Nr - 1, 0, -1):
            state = self.inverse_round(state, round_keys[i])

        state = self.inverse_final_round(state, round_keys[0])
        return self.to_bytes(state)

    @staticmethod
    def inverse_byte_substitution(state):
        return [[AES.inverse_s_box[b] for b in row] for row in state]

    @staticmethod
    def inverse_shift_rows(state):
        return [
            state[0],
            state[1][-1:] + state[1][:-1],
            state[2][-2:] + state[2][:-2],
            state[3][-3:] + state[3][:-3],
        ]

    @staticmethod
    def inverse_mix_column(state):
        for i in range(4):
            col = [state[j][i] for j in range(4)]
            mixed_col = AES.inverse_mix_single_column(col)
            for j in range(4):
                state[j][i] = mixed_col[j]
        return state

    @staticmethod
    def inverse_mix_single_column(col):
        a0, a1, a2, a3 = col
        r0 = AES.mul_by_0E(a0) ^ AES.mul_by_0B(a1) ^ AES.mul_by_0D(a2) ^ AES.mul_by_09(a3)
        r1 = AES.mul_by_09(a0) ^ AES.mul_by_0E(a1) ^ AES.mul_by_0B(a2) ^ AES.mul_by_0D(a3)
        r2 = AES.mul_by_0D(a0) ^ AES.mul_by_09(a1) ^ AES.mul_by_0E(a2) ^ AES.mul_by_0B(a3)
        r3 = AES.mul_by_0B(a0) ^ AES.mul_by_0D(a1) ^ AES.mul_by_09(a2) ^ AES.mul_by_0E(a3)
        return [r0, r1, r2, r3]

    @staticmethod
    def inverse_round(state, round_key):
        state = AES.add_round_key(state, round_key)
        state = AES.inverse_mix_column(state)
        state = AES.inverse_shift_rows(state)
        state = AES.inverse_byte_substitution(state)
        return state

    @staticmethod
    def inverse_final_round(state, round_key):
        state = AES.add_round_key(state, round_key)
        state = AES.inverse_shift_rows(state)
        state = AES.inverse_byte_substitution(state)
        return state




