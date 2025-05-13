from aes import AES
import os
import random

def hamming_distance(a, b):
    distance = 0
    for byte1, byte2 in zip(a, b):
        xor_result = byte1 ^ byte2
        bits_different = bin(xor_result).count('1')
        distance += bits_different
    return distance

def flip_bit(x: bytes, index: int) -> bytes:
    byte_index = index // 8
    bit_index = index % 8
    flipped_byte = x[byte_index] ^ (1 << (7 - bit_index))
    return x[:byte_index] + bytes([flipped_byte]) + x[byte_index + 1:]


def aes_diffusion(num_round=None):
    plaintext = os.urandom(16)
    key = os.urandom(16)

    bit_index = random.randint(0, 127)
    flipped_plaintext = flip_bit(plaintext, bit_index)

    aes = AES(key)
    ciphertext = aes.partially_encrypt(plaintext, num_round)
    flipped_ciphertext = aes.partially_encrypt(flipped_plaintext, num_round)
    
    return hamming_distance(ciphertext, flipped_ciphertext)

def aes_confusion(num_round=None):
    plaintext = os.urandom(16)
    key = os.urandom(16)

    bit_index = random.randint(0, 127)
    flipped_key = flip_bit(key, bit_index)

    aes = AES(key)
    flipped_aes = AES(flipped_key)
    
    ciphertext = aes.partially_encrypt(plaintext, num_round)
    flipped_ciphertext = flipped_aes.partially_encrypt(plaintext, num_round)
    
    return hamming_distance(ciphertext, flipped_ciphertext)