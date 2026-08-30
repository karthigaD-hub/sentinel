import os
import threading
from app.quantum.schemas import KyberKeygenResult, KyberEncapsulateResult, KyberDecapsulateResult


class KyberService:
    def __init__(self) -> None:
        self._lib = None
        self._key_store: dict[str, bytes] = {}
        self._lock = threading.Lock()
        self._counter = 0

    def _load_lib(self) -> None:
        if self._lib is not None:
            return
        try:
            import pqcrypto
            self._lib = pqcrypto
        except ImportError:
            pass

    @property
    def available(self) -> bool:
        self._load_lib()
        if self._lib is not None:
            return True
        return False

    def _store_key(self, key_bytes: bytes) -> str:
        with self._lock:
            self._counter += 1
            handle = f"key_{self._counter}_{os.urandom(4).hex()}"
            self._key_store[handle] = key_bytes
            return handle

    def _retrieve_key(self, handle: str) -> bytes | None:
        with self._lock:
            return self._key_store.get(handle)

    def _delete_key(self, handle: str) -> None:
        with self._lock:
            self._key_store.pop(handle, None)

    def keygen(self) -> KyberKeygenResult:
        if not self.available:
            return KyberKeygenResult(
                available=False,
                reason="Post-quantum Kyber library not installed. Install: pip install pqcrypto",
            )
        try:
            from pqcrypto.kem import kyber768
            public_key, secret_key = kyber768.keygen()
            handle = self._store_key(bytes(secret_key))
            return KyberKeygenResult(
                available=True,
                public_key=bytes(public_key).hex(),
                private_key_handle=handle,
            )
        except Exception as exc:
            return KyberKeygenResult(available=False, reason=str(exc))

    def encapsulate(self, public_key_hex: str) -> KyberEncapsulateResult:
        if not self.available:
            return KyberEncapsulateResult(
                available=False,
                reason="Post-quantum Kyber library not installed. Install: pip install pqcrypto",
            )
        try:
            from pqcrypto.kem import kyber768
            public_key = bytes.fromhex(public_key_hex)
            ciphertext, shared_secret = kyber768.encaps(public_key)
            handle = self._store_key(bytes(shared_secret))
            return KyberEncapsulateResult(
                available=True,
                ciphertext=bytes(ciphertext).hex(),
                shared_secret_handle=handle,
            )
        except Exception as exc:
            return KyberEncapsulateResult(available=False, reason=str(exc))

    def decapsulate(self, private_key_handle: str, ciphertext_hex: str) -> KyberDecapsulateResult:
        if not self.available:
            return KyberDecapsulateResult(
                available=False,
                reason="Post-quantum Kyber library not installed. Install: pip install pqcrypto",
            )
        secret_key = self._retrieve_key(private_key_handle)
        if secret_key is None:
            return KyberDecapsulateResult(
                available=False,
                reason="Private key handle not found or expired",
            )
        try:
            from pqcrypto.kem import kyber768
            ciphertext = bytes.fromhex(ciphertext_hex)
            shared_secret = kyber768.decaps(secret_key, ciphertext)
            handle = self._store_key(bytes(shared_secret))
            return KyberDecapsulateResult(
                available=True,
                shared_secret_handle=handle,
                verified=True,
            )
        except Exception as exc:
            return KyberDecapsulateResult(available=False, reason=str(exc))

    def get_shared_secret(self, handle: str) -> bytes | None:
        return self._retrieve_key(handle)

    def clear_keys(self) -> None:
        with self._lock:
            self._key_store.clear()


kyber_service = KyberService()
