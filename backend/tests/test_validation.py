from pydantic import ValidationError
import pytest
from app.schemas import UserCreate

def test_password_minimum_length() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="person@example.com", password="short")
