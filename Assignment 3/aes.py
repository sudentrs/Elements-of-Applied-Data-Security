import numpy as np

class AES:
    def __init__(self, key: bytes):

        if isinstance(key, str):
            key = key.encode('utf-8')

        if len(key) != 16:
            raise ValueError("the key should be 16 bytes!!!!")

        self.key = key
        self.loop = 10 
        self.round_keys = self.key_expansion()

    def encrypt(self, plaintext: bytes):
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        if len(plaintext) != 16:
            raise ValueError("input should be 16 bytes!!!")

        state = np.frombuffer(plaintext, dtype=np.uint8).reshape(4, 4).T
        state = self.add_round_key(state, self.round_keys[0])

        for round_num in range(1, self.loop):
            state = self.round(state, self.round_keys[round_num])

        state = self.final_round(state, self.round_keys[self.loop])
        return state.T.flatten().tobytes()

    def key_expansion(self):
        key_words = [list(self.key[i:i+4]) for i in range(0, 16, 4)]
        sbox = self.s_box().flatten()
        rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

        for i in range(4, 44):
            temp = key_words[i - 1]
            if i % 4 == 0:
                temp = [sbox[b] for b in temp[1:] + temp[:1]]
                temp[0] ^= rcon[(i // 4) - 1]
            new_word = [temp[j] ^ key_words[i - 4][j] for j in range(4)]
            key_words.append(new_word)

        round_keys = [np.array(key_words[i*4:(i+1)*4]).T for i in range(11)]
        return round_keys

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
    def add_round_key(state, round_key):
        return state ^ round_key

    @staticmethod
    def byte_substitution(state):
        sbox = AES.s_box()
        return sbox[state]

    @staticmethod
    def shift_rows(state):
        return np.array([np.roll(state[i], -i) for i in range(4)])

    @staticmethod
    def mix_column(state):
        def xtime(a):
            return ((a << 1) ^ (0x1b if a & 0x80 else 0x00)) & 0xFF

        def mix_single_column(col):
            t = col[0] ^ col[1] ^ col[2] ^ col[3]
            u = col[0]
            col[0] ^= t ^ xtime(col[0] ^ col[1])
            col[1] ^= t ^ xtime(col[1] ^ col[2])
            col[2] ^= t ^ xtime(col[2] ^ col[3])
            col[3] ^= t ^ xtime(col[3] ^ u)
            return col

        mixed = [mix_single_column(state[:, i].copy()) for i in range(4)]
        return np.array(mixed).T

    @staticmethod
    def s_box():
        full_sbox = [ 0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
                      0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,] + [0] * (256 - 16)
        return np.array(full_sbox, dtype=np.uint8)
