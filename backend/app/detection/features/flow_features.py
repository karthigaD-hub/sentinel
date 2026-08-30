from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections.abc import Sequence


@dataclass
class _FlowState:
    source_ip: str = ""
    destination_ip: str = ""
    protocol: str = "OTHER"
    source_port: int | None = None
    destination_port: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    fwd_packets: int = 0
    bwd_packets: int = 0
    fwd_lengths: list[int] = field(default_factory=list)
    bwd_lengths: list[int] = field(default_factory=list)
    fwd_header_lengths: list[int] = field(default_factory=list)
    bwd_header_lengths: list[int] = field(default_factory=list)
    packet_lengths: list[int] = field(default_factory=list)
    fwd_timestamps: list[float] = field(default_factory=list)
    bwd_timestamps: list[float] = field(default_factory=list)
    flow_timestamps: list[float] = field(default_factory=list)
    syn_count: int = 0
    ack_count: int = 0
    fin_count: int = 0
    rst_count: int = 0
    psh_count: int = 0
    urg_count: int = 0
    active_times: list[float] = field(default_factory=list)
    idle_times: list[float] = field(default_factory=list)
    last_active_at: float | None = None


class FlowFeatures:
    def __init__(self) -> None:
        self._flows: dict[str, _FlowState] = {}

    @staticmethod
    def _make_key(meta) -> str:
        return (
            f"{meta.source_ip}:{meta.source_port or 0}-"
            f"{meta.destination_ip}:{meta.destination_port or 0}-"
            f"{meta.protocol}"
        )

    def add_packet(self, meta) -> str:
        key = self._make_key(meta)
        if key not in self._flows:
            self._flows[key] = _FlowState(
                source_ip=meta.source_ip,
                destination_ip=meta.destination_ip,
                protocol=meta.protocol,
                source_port=meta.source_port,
                destination_port=meta.destination_port,
                started_at=meta.timestamp,
            )
        flow = self._flows[key]
        flow.ended_at = meta.timestamp

        ts = meta.timestamp.timestamp()
        flow.flow_timestamps.append(ts)

        is_forward = True
        if flow.source_ip != meta.source_ip:
            is_forward = False

        if is_forward:
            flow.fwd_packets += 1
            flow.fwd_lengths.append(meta.length)
            flow.fwd_timestamps.append(ts)
            if meta.ttl is not None:
                flow.fwd_header_lengths.append(meta.length - meta.length)
        else:
            flow.bwd_packets += 1
            flow.bwd_lengths.append(meta.length)
            flow.bwd_timestamps.append(ts)

        flow.packet_lengths.append(meta.length)

        if meta.flags:
            flags = meta.flags.upper()
            if "S" in flags:
                flow.syn_count += 1
            if "A" in flags:
                flow.ack_count += 1
            if "F" in flags:
                flow.fin_count += 1
            if "R" in flags:
                flow.rst_count += 1
            if "P" in flags:
                flow.psh_count += 1
            if "U" in flags:
                flow.urg_count += 1

        if flow.last_active_at is not None:
            gap = ts - flow.last_active_at
            if gap > 1.0:
                flow.idle_times.append(gap)
            else:
                flow.active_times.append(gap)
        flow.last_active_at = ts
        return key

    def get_flow_state(self, key: str) -> _FlowState | None:
        return self._flows.get(key)

    def get_all_keys(self) -> list[str]:
        return list(self._flows.keys())

    def reset(self) -> None:
        self._flows.clear()


def _safe_mean(values: Sequence[float | int]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def _safe_std(values: Sequence[float | int]) -> float:
    if len(values) < 2:
        return 0.0
    import math
    m = _safe_mean(values)
    variance = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(variance)


def _iat_stats(timestamps: list[float]) -> tuple[float, float, float]:
    if len(timestamps) < 2:
        return 0.0, 0.0, 0.0
    iats = [timestamps[i + 1] - timestamps[i] for i in range(len(timestamps) - 1)]
    total = sum(iats)
    return total, _safe_mean(iats), _safe_std(iats)
