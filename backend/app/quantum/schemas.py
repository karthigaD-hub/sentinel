from pydantic import BaseModel


class KyberKeygenResult(BaseModel):
    available: bool
    public_key: str | None = None
    private_key_handle: str | None = None
    reason: str | None = None


class KyberEncapsulateResult(BaseModel):
    available: bool
    ciphertext: str | None = None
    shared_secret_handle: str | None = None
    reason: str | None = None


class KyberDecapsulateResult(BaseModel):
    available: bool
    shared_secret_handle: str | None = None
    verified: bool = False
    reason: str | None = None


class SecureAlertPayload(BaseModel):
    algorithm: str
    ciphertext: str
    nonce: str
    key_establishment: str
    shared_secret_verified: bool
