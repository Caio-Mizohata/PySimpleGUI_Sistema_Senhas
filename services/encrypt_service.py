from Crypto.Cipher import AES
import base64

class DecryptionError(Exception):
    pass

class EncryptService:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: str) -> str:
        try:
            cipher = AES.new(self.key, AES.MODE_EAX)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
            return base64.b64encode(cipher.nonce + tag + ciphertext).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Falha na encriptação: {str(e)}")

    def decrypt(self, encrypted_text: str) -> str:
        try:
            data = base64.b64decode(encrypted_text)
            nonce = data[:16] 
            tag = data[16:32] 
            ciphertext = data[32:] 
            cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce) 
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext.decode("utf-8")
        except Exception as e:
            raise DecryptionError(f"Falha na decriptação: {str(e)}")
