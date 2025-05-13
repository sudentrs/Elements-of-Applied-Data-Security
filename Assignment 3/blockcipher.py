import os
from Crypto.Util.Padding import pad, unpad

class BlockCipher:
    def __init__(self, key, iv=None, algorithm=None, mode='ECB'):
        self.key = key
        self.algorithm = algorithm(key)
        self.mode = mode

        if iv is None:
            self.iv = os.urandom(16)  # Generate random IV for CBC, CFB, OFB
        else:
            self.iv = iv

    def pad(self, plaintext, block_size=16):
        return pad(plaintext, block_size)

    def unpad(self, ciphertext, block_size=16):
        return unpad(ciphertext, block_size)

    def encrypt(self, plaintext):
        plaintext = self.pad(plaintext)

        if self.mode == 'ECB':
            return self.ecb_encrypt(plaintext)
        elif self.mode == 'CBC':
            return self.cbc_encrypt(plaintext)
        elif self.mode == 'CFB':
            return self.cfb_encrypt(plaintext)
        elif self.mode == 'OFB':
            return self.ofb_encrypt(plaintext)
        else:
            raise ValueError("Unsupported mode")

    def decrypt(self, ciphertext):
        if self.mode == 'ECB':
            decrypted = self.ecb_decrypt(ciphertext)
        elif self.mode == 'CBC':
            decrypted = self.cbc_decrypt(ciphertext)
        elif self.mode == 'CFB':
            decrypted = self.cfb_decrypt(ciphertext)
        elif self.mode == 'OFB':
            decrypted = self.ofb_decrypt(ciphertext)
        else:
            raise ValueError("Unsupported mode")

        return self.unpad(decrypted)

    def ecb_encrypt(self, plaintext):
        return self.algorithm.encrypt(plaintext)

    def ecb_decrypt(self, ciphertext):
        return self.algorithm.decrypt(ciphertext)

    def cbc_encrypt(self, plaintext):
        ciphertext = bytearray()
        previous_block = self.iv

        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            xor_block = bytes([b ^ p for b, p in zip(block, previous_block)])
            encrypted_block = self.algorithm.encrypt(xor_block)
            ciphertext.extend(encrypted_block)
            previous_block = encrypted_block

        return bytes(ciphertext)

    def cbc_decrypt(self, ciphertext):
        plaintext = bytearray()
        previous_block = self.iv

        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            decrypted_block = self.algorithm.decrypt(block)
            xor_block = bytes([b ^ p for b, p in zip(decrypted_block, previous_block)])
            plaintext.extend(xor_block)
            previous_block = block

        return bytes(plaintext)

    def ofb_encrypt(self, plaintext):
        ciphertext = bytearray()
        output = self.iv

        for i in range(0, len(plaintext), 16):
            output = self.algorithm.encrypt(output)
            block = plaintext[i:i+16]
            xor_block = bytes([b ^ o for b, o in zip(block, output)])
            ciphertext.extend(xor_block)

        return bytes(ciphertext)

    def ofb_decrypt(self, ciphertext):
        return self.ofb_encrypt(ciphertext)  # OFB decryption is identical

    def cfb_encrypt(self, plaintext):
        ciphertext = bytearray()
        feedback = self.iv

        for i in range(0, len(plaintext), 16):
            feedback = self.algorithm.encrypt(feedback)
            block = plaintext[i:i+16]
            xor_block = bytes([b ^ f for b, f in zip(block, feedback)])
            ciphertext.extend(xor_block)
            feedback = xor_block

        return bytes(ciphertext)

    def cfb_decrypt(self, ciphertext):
        plaintext = bytearray()
        feedback = self.iv

        for i in range(0, len(ciphertext), 16):
            feedback = self.algorithm.encrypt(feedback)
            block = ciphertext[i:i+16]
            xor_block = bytes([b ^ f for b, f in zip(block, feedback)])
            plaintext.extend(xor_block)
            feedback = block

        return bytes(plaintext)
