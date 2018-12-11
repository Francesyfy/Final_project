import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        msg = base64.b64encode(iv + cipher.encrypt(raw))
        return str(msg)[1:]

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return str(self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8'))

    def _pad(self, s):
        return s + (len(self.key) - len(s) % len(self.key)) * chr(len(self.key) - len(s) % len(self.key))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
msg = "hi"
encry = AESCipher("2333").encrypt(msg)
print(encry)
decry = AESCipher("2333").decrypt(encry)
print(decry)
