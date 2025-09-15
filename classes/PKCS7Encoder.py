import binascii
import base64
import json
from io import StringIO
from Crypto.Cipher import AES

class PKCS7Encoder:
    def __init__(self):
        self.block_size = 16
        self.aes_mode = AES.MODE_ECB

    def encrypt(self, raw, key):
        new_data = raw.encode("latin-1")
        key_enc = key.encode().ljust(16, b'\0')
        new_data = self.addpad(new_data)
        cipher = AES.new(key_enc, self.aes_mode)
        return (base64.b64encode(cipher.encrypt(new_data))).decode('utf-8')

    def decrypt(self, enc, key):
        new_data = enc.encode("utf-16-be")
        key_enc = key.encode().ljust(16, b'\0')
        new_data = base64.b64decode(new_data)
        cipher = AES.new(key_enc, self.aes_mode)
        return (self.strippad(cipher.decrypt(new_data)))

    def strippad(self, text):
        nl = len(text)
        te = str(text[-1])
        te = te.encode("latin-1")
        val = int(te)
        if val > self.block_size:
            raise ValueError('Input is not padded or padding is corrupt')
        l = nl - val
        return text[:l]

    def addpad(self, text):
        l = len(text)
        output = StringIO()
        val = self.block_size - (l % self.block_size)
        for _ in range(val):
            output.write('%02x' % val)
        return text + binascii.unhexlify(output.getvalue())
