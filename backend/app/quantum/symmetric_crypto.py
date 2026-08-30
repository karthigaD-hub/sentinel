import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SymmetricCryptoService:
    @staticmethod
    def encrypt(plaintext: bytes, shared_secret: bytes) -> dict:
        nonce = os.urandom(12)
        aesgcm = AESGCM(shared_secret)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return {
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
        }

    @staticmethod
    def decrypt(ciphertext_b64: str, nonce_b64: str, shared_secret: bytes) -> bytes:
        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        aesgcm = AESGCM(shared_secret)
        return aesgcm.decrypt(nonce, ciphertext, None)

    @staticmethod
    def derive_key(shared_secret: bytes) -> bytes:
        import hashlib
        return hashlib.sha256(shared_secret).digest()[:32]


symmetric_crypto_service = SymmetricCryptoService()
