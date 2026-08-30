import json
from pathlib import Path
import numpy as np
from app.detection.features.feature_schema import FEATURE_SCHEMA, PROTOCOL_MAP
from app.detection.features.flow_features import FlowFeatures, _safe_mean, _safe_std, _iat_stats


def extract_feature_vector(flow: FlowFeatures, flow_key: str) -> list[float]:
    state = flow.get_flow_state(flow_key)
    if state is None:
        return [0.0] * len(FEATURE_SCHEMA)

    duration = 0.0
    if state.started_at and state.ended_at:
        duration = (state.ended_at - state.started_at).total_seconds()
    if duration <= 0:
        duration = 1e-6

    all_lengths = state.packet_lengths
    fwd_lengths = state.fwd_lengths
    bwd_lengths = state.bwd_lengths

    total_fwd = sum(fwd_lengths) if fwd_lengths else 0
    total_bwd = sum(bwd_lengths) if bwd_lengths else 0

    fwd_iat_total, fwd_iat_mean, fwd_iat_std = _iat_stats(state.fwd_timestamps)
    bwd_iat_total, bwd_iat_mean, bwd_iat_std = _iat_stats(state.bwd_timestamps)
    flow_iat_total, flow_iat_mean, flow_iat_std = _iat_stats(state.flow_timestamps)

    flow_bytes = total_fwd + total_bwd
    flow_packets = state.fwd_packets + state.bwd_packets
    flow_bps = flow_bytes / duration
    flow_pps = flow_packets / duration

    down_up = (state.bwd_packets / state.fwd_packets) if state.fwd_packets > 0 else 0.0

    vector = [
        duration,
        PROTOCOL_MAP.get(state.protocol, 0),
        state.fwd_packets,
        state.bwd_packets,
        total_fwd,
        total_bwd,
        max(fwd_lengths) if fwd_lengths else 0.0,
        min(fwd_lengths) if fwd_lengths else 0.0,
        _safe_mean(fwd_lengths),
        _safe_std(fwd_lengths),
        max(bwd_lengths) if bwd_lengths else 0.0,
        min(bwd_lengths) if bwd_lengths else 0.0,
        _safe_mean(bwd_lengths),
        _safe_std(bwd_lengths),
        flow_bps,
        flow_pps,
        min(all_lengths) if all_lengths else 0.0,
        max(all_lengths) if all_lengths else 0.0,
        _safe_mean(all_lengths),
        _safe_std(all_lengths),
        (flow_bytes / flow_packets) if flow_packets > 0 else 0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        fwd_iat_total,
        fwd_iat_mean,
        fwd_iat_std,
        bwd_iat_total,
        bwd_iat_mean,
        bwd_iat_std,
        flow_iat_mean,
        flow_iat_std,
        max([0.0]),
        min([0.0]),
        state.syn_count,
        state.ack_count,
        state.fin_count,
        state.rst_count,
        state.psh_count,
        state.urg_count,
        down_up,
        (flow_bytes / flow_packets) if flow_packets > 0 else 0.0,
        _safe_mean(state.active_times),
        _safe_std(state.active_times),
        max(state.active_times) if state.active_times else 0.0,
        min(state.active_times) if state.active_times else 0.0,
        _safe_mean(state.idle_times),
        _safe_std(state.idle_times),
        max(state.idle_times) if state.idle_times else 0.0,
        min(state.idle_times) if state.idle_times else 0.0,
    ]
    return vector


class Preprocessor:
    def __init__(self) -> None:
        self.scaler = None
        self.label_encoder = None
        self.feature_names: list[str] = list(FEATURE_SCHEMA)

    def fit(self, X: np.ndarray, y: np.ndarray | None = None) -> "Preprocessor":
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        self.scaler.fit(X)
        if y is not None:
            from sklearn.preprocessing import LabelEncoder
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(y)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.scaler is None:
            raise RuntimeError("Preprocessor has not been fitted")
        return self.scaler.transform(X)

    def fit_transform(self, X: np.ndarray, y: np.ndarray | None = None) -> np.ndarray:
        self.fit(X, y)
        return self.transform(X)

    def inverse_label(self, encoded: int) -> str:
        if self.label_encoder is None:
            raise RuntimeError("Label encoder has not been fitted")
        return str(self.label_encoder.inverse_transform([encoded])[0])

    def save(self, path: str) -> None:
        import joblib
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"scaler": self.scaler, "label_encoder": self.label_encoder, "feature_names": self.feature_names}, path)

    @classmethod
    def load(cls, path: str) -> "Preprocessor":
        import joblib
        data = joblib.load(path)
        obj = cls()
        obj.scaler = data["scaler"]
        obj.label_encoder = data["label_encoder"]
        obj.feature_names = data["feature_names"]
        return obj
