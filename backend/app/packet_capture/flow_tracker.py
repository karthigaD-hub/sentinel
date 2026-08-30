from datetime import datetime, timezone
from app.packet_capture.schemas import FlowKey, FlowStatistics


class FlowTracker:
    def __init__(self) -> None:
        self._flows: dict[str, dict] = {}

    @staticmethod
    def _make_key(source_ip: str, destination_ip: str, source_port: int | None, destination_port: int | None, protocol: str) -> str:
        return f"{source_ip}:{source_port or 0}-{destination_ip}:{destination_port or 0}-{protocol}"

    def aggregate_flow(self, packet_meta) -> FlowStatistics:
        key_str = self._make_key(
            packet_meta.source_ip,
            packet_meta.destination_ip,
            packet_meta.source_port,
            packet_meta.destination_port,
            packet_meta.protocol,
        )
        now = datetime.now(timezone.utc)
        if key_str not in self._flows:
            self._flows[key_str] = {
                "source_ip": packet_meta.source_ip,
                "destination_ip": packet_meta.destination_ip,
                "protocol": packet_meta.protocol,
                "source_port": packet_meta.source_port,
                "destination_port": packet_meta.destination_port,
                "started_at": packet_meta.timestamp,
                "ended_at": None,
                "packet_count": 0,
                "byte_count": 0,
            }
        flow = self._flows[key_str]
        flow["packet_count"] += 1
        flow["byte_count"] += packet_meta.length
        flow["ended_at"] = now
        duration = (now - flow["started_at"]).total_seconds() if flow["started_at"] else 0.0
        return FlowStatistics(
            source_ip=flow["source_ip"],
            destination_ip=flow["destination_ip"],
            protocol=flow["protocol"],
            source_port=flow["source_port"],
            destination_port=flow["destination_port"],
            started_at=flow["started_at"],
            ended_at=flow["ended_at"],
            packet_count=flow["packet_count"],
            byte_count=flow["byte_count"],
            duration_seconds=duration,
        )

    def get_active_flows(self) -> list[FlowStatistics]:
        result: list[FlowStatistics] = []
        for flow in self._flows.values():
            duration = 0.0
            if flow["started_at"]:
                end = flow["ended_at"] or datetime.now(timezone.utc)
                duration = (end - flow["started_at"]).total_seconds()
            result.append(FlowStatistics(
                source_ip=flow["source_ip"],
                destination_ip=flow["destination_ip"],
                protocol=flow["protocol"],
                source_port=flow["source_port"],
                destination_port=flow["destination_port"],
                started_at=flow["started_at"],
                ended_at=flow["ended_at"],
                packet_count=flow["packet_count"],
                byte_count=flow["byte_count"],
                duration_seconds=duration,
            ))
        return result

    def reset(self) -> None:
        self._flows.clear()
