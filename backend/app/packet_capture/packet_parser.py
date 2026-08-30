from datetime import datetime, timezone
from app.packet_capture.schemas import PacketMetadata


def parse_packet(packet, interface: str) -> PacketMetadata | None:
    try:
        from scapy.layers.inet import IP, TCP, UDP, ICMP
        from scapy.layers.dns import DNS
        from scapy.layers.http import HTTPRequest
    except ImportError:
        return None

    if IP not in packet:
        return None

    ip_layer = packet[IP]
    source_ip = ip_layer.src
    destination_ip = ip_layer.dst
    protocol = "OTHER"
    source_port: int | None = None
    destination_port: int | None = None
    flags: str | None = None
    ttl: int | None = ip_layer.ttl
    dns_query: str | None = None
    http_method: str | None = None
    http_host: str | None = None
    http_path: str | None = None
    tls_sni: str | None = None

    if TCP in packet:
        protocol = "TCP"
        tcp = packet[TCP]
        source_port = int(tcp.sport)
        destination_port = int(tcp.dport)
        flags = str(tcp.flags)
    elif UDP in packet:
        protocol = "UDP"
        udp = packet[UDP]
        source_port = int(udp.sport)
        destination_port = int(udp.dport)
    elif ICMP in packet:
        protocol = "ICMP"

    if DNS in packet:
        try:
            dns = packet[DNS]
            if dns.qd and dns.qd.qname:
                dns_query = dns.qd.qname.decode("utf-8", errors="replace")
        except Exception:
            pass

    if HTTPRequest in packet:
        try:
            http = packet[HTTPRequest]
            http_method = http.Method.decode("utf-8", errors="replace") if http.Method else None
            http_host = http.Host.decode("utf-8", errors="replace") if http.Host else None
            http_path = http.Path.decode("utf-8", errors="replace") if http.Path else None
        except Exception:
            pass

    if packet.haslayer("TLS"):
        try:
            for layer in packet.layers():
                if hasattr(layer, "server_name") and layer.server_name:
                    tls_sni = layer.server_name
                    break
        except Exception:
            pass

    return PacketMetadata(
        timestamp=datetime.now(timezone.utc),
        interface=interface,
        source_ip=source_ip,
        destination_ip=destination_ip,
        protocol=protocol,
        source_port=source_port,
        destination_port=destination_port,
        length=len(packet),
        flags=flags,
        ttl=ttl,
        dns_query=dns_query,
        http_method=http_method,
        http_host=http_host,
        http_path=http_path,
        tls_sni=tls_sni,
    )
