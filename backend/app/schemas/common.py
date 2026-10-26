from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(default="", max_length=200)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserRead(ORMModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    role: str

    @model_validator(mode="before")
    @classmethod
    def flatten_role(cls, value: object) -> object:
        if hasattr(value, "role") and getattr(value, "role") is not None:
            return {"id": value.id, "email": value.email, "full_name": value.full_name, "is_active": value.is_active, "is_verified": value.is_verified, "role": value.role.name}
        return value

class MessageResponse(BaseModel):
    message: str

class PaginatedResponse(BaseModel):
    items: list
    page: int
    page_size: int
    total: int

class AlertRead(ORMModel):
    id: UUID
    title: str
    severity: str
    status: str
    description: str
    acknowledged_by: UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime

class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str = Field(min_length=1, max_length=10000)

class ChatResponse(BaseModel):
    conversation_id: UUID
    answer: str
    citations: list = []

class RAGQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)
    top_k: int = Field(default=5, ge=1, le=50)
