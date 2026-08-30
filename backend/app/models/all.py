from datetime import datetime
from uuid import UUID
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, UUIDTimestampMixin

class Role(UUIDTimestampMixin, Base):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String(50), unique=True)
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list)
    users: Mapped[list["User"]] = relationship(back_populates="role")

class User(UUIDTimestampMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(200), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("roles.id"))
    role: Mapped[Role] = relationship(back_populates="users")
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Permission(UUIDTimestampMixin, Base):
    __tablename__ = "permissions"
    name: Mapped[str] = mapped_column(String(100), unique=True)

class RefreshToken(UUIDTimestampMixin, Base):
    __tablename__ = "refresh_tokens"
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    family_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    user: Mapped[User] = relationship(back_populates="refresh_tokens")

class VerificationToken(UUIDTimestampMixin, Base):
    __tablename__ = "verification_tokens"
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Packet(UUIDTimestampMixin, Base):
    __tablename__ = "packets"
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    interface: Mapped[str] = mapped_column(String(100))
    source_ip: Mapped[str] = mapped_column(String(255))
    destination_ip: Mapped[str] = mapped_column(String(255))
    protocol: Mapped[str] = mapped_column(String(30))
    source_port: Mapped[int | None] = mapped_column(Integer)
    destination_port: Mapped[int | None] = mapped_column(Integer)
    length: Mapped[int] = mapped_column(Integer)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

class Flow(UUIDTimestampMixin, Base):
    __tablename__ = "flows"
    source_ip: Mapped[str] = mapped_column(String(255), index=True)
    destination_ip: Mapped[str] = mapped_column(String(255), index=True)
    protocol: Mapped[str] = mapped_column(String(30))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    packet_count: Mapped[int] = mapped_column(Integer, default=0)
    byte_count: Mapped[int] = mapped_column(Integer, default=0)

class Detection(UUIDTimestampMixin, Base):
    __tablename__ = "detections"
    packet_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("packets.id"))
    flow_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("flows.id"))
    label: Mapped[str] = mapped_column(String(100))
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(100))
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    features: Mapped[list["DetectionFeature"]] = relationship(back_populates="detection")
    explanation: Mapped["Explanation | None"] = relationship(back_populates="detection", uselist=False)

class DetectionFeature(UUIDTimestampMixin, Base):
    __tablename__ = "detection_features"
    detection_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("detections.id"))
    name: Mapped[str] = mapped_column(String(150))
    value: Mapped[float] = mapped_column(Float)
    importance: Mapped[float | None] = mapped_column(Float)
    detection: Mapped[Detection] = relationship(back_populates="features")

class Explanation(UUIDTimestampMixin, Base):
    __tablename__ = "explanations"
    detection_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("detections.id"), unique=True)
    method: Mapped[str] = mapped_column(String(50))
    values: Mapped[dict] = mapped_column(JSON)
    detection: Mapped[Detection] = relationship(back_populates="explanation")

class Alert(UUIDTimestampMixin, Base):
    __tablename__ = "alerts"
    detection_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("detections.id"))
    title: Mapped[str] = mapped_column(String(250))
    severity: Mapped[str] = mapped_column(String(30), index=True)
    status: Mapped[str] = mapped_column(String(30), default="open", index=True)
    description: Mapped[str] = mapped_column(Text)
    acknowledged_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class ThreatIntelReference(UUIDTimestampMixin, Base):
    __tablename__ = "threat_intel_references"
    source: Mapped[str] = mapped_column(String(100))
    external_id: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str] = mapped_column(String(500))
    url: Mapped[str | None] = mapped_column(String(1000))
    content: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class RAGDocument(UUIDTimestampMixin, Base):
    __tablename__ = "rag_documents"
    source: Mapped[str] = mapped_column(String(200))
    external_id: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    embedding: Mapped[list[float] | None] = mapped_column(JSON)

class AssistantConversation(UUIDTimestampMixin, Base):
    __tablename__ = "assistant_conversations"
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(300), default="New conversation")
    messages: Mapped[list["AssistantMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")

class AssistantMessage(UUIDTimestampMixin, Base):
    __tablename__ = "assistant_messages"
    conversation_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("assistant_conversations.id"))
    role: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    citations: Mapped[list] = mapped_column(JSON, default=list)
    conversation: Mapped[AssistantConversation] = relationship(back_populates="messages")

class QuantumSecurityEvent(UUIDTimestampMixin, Base):
    __tablename__ = "quantum_security_events"
    event_type: Mapped[str] = mapped_column(String(100))
    algorithm: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    details: Mapped[dict] = mapped_column(JSON, default=dict)

class SystemEvent(UUIDTimestampMixin, Base):
    __tablename__ = "system_events"
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    severity: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

class SecureAlert(UUIDTimestampMixin, Base):
    __tablename__ = "secure_alerts"
    alert_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("alerts.id"))
    algorithm: Mapped[str] = mapped_column(String(100))
    ciphertext: Mapped[str] = mapped_column(Text)
    nonce: Mapped[str] = mapped_column(String(64))
    key_establishment: Mapped[str] = mapped_column(String(50))
    shared_secret_verified: Mapped[bool] = mapped_column(Boolean, default=False)

Index("ix_refresh_tokens_user_family", RefreshToken.user_id, RefreshToken.family_id)
UniqueConstraint("source", "external_id", name="uq_threat_intel_source_external")
