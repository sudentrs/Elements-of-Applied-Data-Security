import os
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES

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
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.encrypt(plaintext)

    def cbc_decrypt(self, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.decrypt(ciphertext)

    def cfb_encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        return cipher.encrypt(plaintext)

    def cfb_decrypt(self, ciphertext):
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv)
        return cipher.decrypt(ciphertext)

    def ofb_encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_OFB, self.iv)
        return cipher.encrypt(plaintext)

    def ofb_decrypt(self, ciphertext):
        cipher = AES.new(self.key, AES.MODE_OFB, self.iv)
        return cipher.decrypt(ciphertext)
