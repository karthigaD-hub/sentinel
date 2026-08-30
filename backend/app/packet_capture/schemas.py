from datetime import datetime
from pydantic import BaseModel, ConfigDict

class InterfaceInfo(BaseModel):
    name: str
    is_up: bool = False
    addresses: list[str] = []

class PacketMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    timestamp: datetime
    interface: str
    source_ip: str
    destination_ip: str
    protocol: str
    source_port: int | None = None
    destination_port: int | None = None
    length: int
    flags: str | None = None
    ttl: int | None = None
    dns_query: str | None = None
    http_method: str | None = None
    http_host: str | None = None
    http_path: str | None = None
    tls_sni: str | None = None

class FlowKey(BaseModel):
    source_ip: str
    destination_ip: str
    source_port: int | None
    destination_port: int | None
    protocol: str

class FlowStatistics(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str
    source_port: int | None
    destination_port: int | None
    started_at: datetime
    ended_at: datetime | None
    packet_count: int
    byte_count: int
    duration_seconds: float

class CaptureStatus(BaseModel):
    available: bool
    running: bool = False
    interface: str | None = None
    reason: str | None = None
    packets_captured: int = 0
