from app.core.security_config import hash_password, verify_password

def test_password_hash_round_trip() -> None:
    hashed = hash_password("a-secure-password-123")
    assert hashed != "a-secure-password-123"
    assert verify_password("a-secure-password-123", hashed)
    assert not verify_password("wrong-password", hashed)
