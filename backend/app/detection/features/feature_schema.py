FEATURE_SCHEMA = [
    "duration",
    "protocol_number",
    "total_fwd_packets",
    "total_bwd_packets",
    "total_length_fwd",
    "total_length_bwd",
    "fwd_packet_length_max",
    "fwd_packet_length_min",
    "fwd_packet_length_mean",
    "fwd_packet_length_std",
    "bwd_packet_length_max",
    "bwd_packet_length_min",
    "bwd_packet_length_mean",
    "bwd_packet_length_std",
    "flow_bytes_per_second",
    "flow_packets_per_second",
    "min_packet_length",
    "max_packet_length",
    "mean_packet_length",
    "std_packet_length",
    "avg_packet_size",
    "fwd_header_length",
    "bwd_header_length",
    "min_header_length",
    "max_header_length",
    "mean_header_length",
    "std_header_length",
    "fwd_iat_total",
    "fwd_iat_mean",
    "fwd_iat_std",
    "bwd_iat_total",
    "bwd_iat_mean",
    "bwd_iat_std",
    "flow_iat_mean",
    "flow_iat_std",
    "flow_iat_max",
    "flow_iat_min",
    "syn_flag_count",
    "ack_flag_count",
    "fin_flag_count",
    "rst_flag_count",
    "psh_flag_count",
    "urg_flag_count",
    "down_up_ratio",
    "average_packet_size",
    "active_mean",
    "active_std",
    "active_max",
    "active_min",
    "idle_mean",
    "idle_std",
    "idle_max",
    "idle_min",
]

PROTOCOL_MAP = {"TCP": 6, "UDP": 17, "ICMP": 1, "OTHER": 0}

FEATURE_COUNT = len(FEATURE_SCHEMA)


def get_feature_index(name: str) -> int:
    return FEATURE_SCHEMA.index(name)


def validate_feature_vector(vector: list[float]) -> bool:
    return len(vector) == FEATURE_COUNT
