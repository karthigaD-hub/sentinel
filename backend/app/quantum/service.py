from app.core.config import settings
from app.quantum.kyber_service import kyber_service, KyberService
from app.quantum.symmetric_crypto import symmetric_crypto_service, SymmetricCryptoService
from app.quantum.schemas import KyberKeygenResult, KyberEncapsulateResult, KyberDecapsulateResult, SecureAlertPayload


class QuantumService:
    def __init__(self) -> None:
        self.kyber = kyber_service
        self.crypto = symmetric_crypto_service

    @property
    def available(self) -> bool:
        return self.kyber.available

    def status(self) -> dict[str, object]:
        return {
            "kyber_available": self.kyber.available,
            "kyber_variant": settings.quantum_kyber_variant,
            "aes_gcm_available": True,
        }

    def keygen(self) -> KyberKeygenResult:
        return self.kyber.keygen()

    def encapsulate(self, public_key_hex: str) -> KyberEncapsulateResult:
        return self.kyber.encapsulate(public_key_hex)

    def decapsulate(self, private_key_handle: str, ciphertext_hex: str) -> KyberDecapsulateResult:
        return self.kyber.decapsulate(private_key_handle, ciphertext_hex)

    def encrypt_alert(self, alert_data: bytes, shared_secret: bytes) -> SecureAlertPayload:
        key = self.crypto.derive_key(shared_secret)
        result = self.crypto.encrypt(alert_data, key)
        return SecureAlertPayload(
            algorithm="Kyber768+AES-256-GCM",
            ciphertext=result["ciphertext"],
            nonce=result["nonce"],
            key_establishment="kyber768",
            shared_secret_verified=True,
        )

    def decrypt_alert(self, ciphertext_b64: str, nonce_b64: str, shared_secret: bytes) -> bytes:
        key = self.crypto.derive_key(shared_secret)
        return self.crypto.decrypt(ciphertext_b64, nonce_b64, key)


quantum_service = QuantumService()
