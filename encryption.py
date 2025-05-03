from pyfingerprint.pyfingerprint import PyFingerprint
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

class Encryption:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, data: str) -> str:
        try:
            iv = os.urandom(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_data = pad(data.encode(), AES.block_size)
            ct_bytes = cipher.encrypt(padded_data)
            return base64.b64encode(iv + ct_bytes).decode('utf-8')
        except (ValueError, KeyError) as e:
            print(f"Encryption error: {e}")
            return None

    def decrypt(self, encrypted: str) -> str:
        try:
            encrypted_data = base64.b64decode(encrypted.encode())
            iv = encrypted_data[:AES.block_size]
            ciphertext = encrypted_data[AES.block_size:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
            return decrypted_data.decode()
        except (ValueError, KeyError) as e:
            print(f"Decryption error: {e}")
            return None