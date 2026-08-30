"""Integration tests for Q-Sentinel detection, RAG, and quantum modules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import numpy as np
import pytest


class TestFeatureSchema:
    def test_feature_count(self):
        from app.detection.features.feature_schema import FEATURE_SCHEMA, FEATURE_COUNT
        assert FEATURE_COUNT == 52
        assert len(FEATURE_SCHEMA) == 52

    def test_protocol_map(self):
        from app.detection.features.feature_schema import PROTOCOL_MAP
        assert PROTOCOL_MAP["TCP"] == 6
        assert PROTOCOL_MAP["UDP"] == 17
        assert PROTOCOL_MAP["ICMP"] == 1

    def test_validate_feature_vector(self):
        from app.detection.features.feature_schema import validate_feature_vector
        assert validate_feature_vector([0.0] * 52) is True
        assert validate_feature_vector([0.0] * 51) is False


class TestFlowFeatures:
    def test_add_packet_and_extract(self):
        from app.detection.features.flow_features import FlowFeatures
        from datetime import datetime, timezone
        from app.packet_capture.schemas import PacketMetadata

        flow = FlowFeatures()
        meta = PacketMetadata(
            timestamp=datetime.now(timezone.utc),
            interface="eth0",
            source_ip="192.168.1.1",
            destination_ip="10.0.0.1",
            protocol="TCP",
            source_port=12345,
            destination_port=80,
            length=64,
            flags="S",
            ttl=64,
        )
        key = flow.add_packet(meta)
        assert key is not None
        assert flow.get_flow_state(key) is not None
        assert flow.get_flow_state(key).fwd_packets == 1


class TestFeatureExtractor:
    def test_extract_feature_vector_length(self):
        from app.detection.features.flow_features import FlowFeatures
        from app.detection.features.feature_extractor import extract_feature_vector
        from app.detection.features.feature_schema import FEATURE_COUNT
        from datetime import datetime, timezone
        from app.packet_capture.schemas import PacketMetadata

        flow = FlowFeatures()
        meta = PacketMetadata(
            timestamp=datetime.now(timezone.utc),
            interface="eth0",
            source_ip="192.168.1.1",
            destination_ip="10.0.0.1",
            protocol="TCP",
            source_port=12345,
            destination_port=80,
            length=64,
            flags="S",
            ttl=64,
        )
        key = flow.add_packet(meta)
        vector = extract_feature_vector(flow, key)
        assert len(vector) == FEATURE_COUNT

    def test_extract_unknown_key_returns_zeros(self):
        from app.detection.features.flow_features import FlowFeatures
        from app.detection.features.feature_extractor import extract_feature_vector
        from app.detection.features.feature_schema import FEATURE_COUNT

        flow = FlowFeatures()
        vector = extract_feature_vector(flow, "nonexistent")
        assert len(vector) == FEATURE_COUNT
        assert all(v == 0.0 for v in vector)


class TestAutoencoder:
    def test_build_and_predict(self):
        from app.detection.training.autoencoder import AutoencoderModel
        model = AutoencoderModel(input_dim=52, encoding_dim=8, hidden_dims=[32, 16])
        model.build()
        assert model.model is not None

        X_train = np.random.randn(100, 52).astype(np.float32)
        result = model.train(X_train, epochs=2, batch_size=32)
        assert "final_loss" in result
        assert model.threshold is not None

        pred = model.predict(X_train[:5])
        assert "anomaly_score" in pred
        assert len(pred["anomaly_score"]) == 5

    def test_save_and_load(self, tmp_path):
        from app.detection.training.autoencoder import AutoencoderModel
        model = AutoencoderModel(input_dim=52, encoding_dim=8, hidden_dims=[32, 16])
        model.build()
        X_train = np.random.randn(100, 52).astype(np.float32)
        model.train(X_train, epochs=1, batch_size=32)
        path = str(tmp_path / "autoencoder.pt")
        model.save(path)

        loaded = AutoencoderModel.load(path)
        assert loaded.threshold is not None
        assert loaded.input_dim == 52

    def test_predict_without_training_raises(self):
        from app.detection.training.autoencoder import AutoencoderModel
        model = AutoencoderModel(input_dim=52, encoding_dim=8)
        with pytest.raises(RuntimeError, match="Model not trained"):
            model.predict(np.zeros((1, 52), dtype=np.float32))


class TestXGBoostModel:
    def test_train_and_predict(self):
        from app.detection.training.xgboost_model import XGBoostModel
        model = XGBoostModel(params={
            "objective": "multi:softprob",
            "max_depth": 3,
            "learning_rate": 0.1,
            "n_estimators": 10,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
        })
        X = np.random.randn(50, 52)
        y = np.random.randint(0, 3, 50)
        metrics = model.train(X, y)
        assert "accuracy" in metrics
        assert "f1" in metrics
        assert "confusion_matrix" in metrics

        result = model.predict(X[:5])
        assert "labels" in result
        assert len(result["labels"]) == 5

    def test_save_and_load(self, tmp_path):
        from app.detection.training.xgboost_model import XGBoostModel
        model = XGBoostModel(params={
            "max_depth": 3,
            "learning_rate": 0.1,
            "n_estimators": 10,
        })
        X = np.random.randn(50, 52)
        y = np.random.randint(0, 2, 50)
        model.train(X, y)
        path = str(tmp_path / "xgboost.joblib")
        model.save(path)

        loaded = XGBoostModel.load(path)
        assert loaded.model is not None
        assert "accuracy" in loaded.metrics

    def test_predict_without_training_raises(self):
        from app.detection.training.xgboost_model import XGBoostModel
        model = XGBoostModel()
        with pytest.raises(RuntimeError, match="Model not trained"):
            model.predict(np.zeros((1, 52)))


class TestSeverityEngine:
    def test_benign_no_anomaly(self):
        from app.detection.engine.severity_engine import SeverityEngine
        sev = SeverityEngine.evaluate("benign", 0.99, False, 0.01, 1.0)
        assert sev == SeverityEngine.INFO

    def test_known_attack_high_confidence(self):
        from app.detection.engine.severity_engine import SeverityEngine
        sev = SeverityEngine.evaluate("ddos", 0.95, True, 5.0, 1.0)
        assert sev == SeverityEngine.CRITICAL

    def test_unknown_anomaly(self):
        from app.detection.engine.severity_engine import SeverityEngine
        sev = SeverityEngine.evaluate("benign", 0.3, True, 4.0, 1.0)
        assert sev == SeverityEngine.HIGH

    def test_medium_severity_attack(self):
        from app.detection.engine.severity_engine import SeverityEngine
        sev = SeverityEngine.evaluate("brute_force", 0.6, True, 2.0, 1.0)
        assert sev == SeverityEngine.MEDIUM


class TestRAGChunker:
    def test_chunk_text_short(self):
        from app.rag.chunker import chunk_text
        result = chunk_text("short text", chunk_size=512, overlap=50)
        assert len(result) == 1

    def test_chunk_text_long(self):
        from app.rag.chunker import chunk_text
        words = "word " * 2000
        result = chunk_text(words.strip(), chunk_size=100, overlap=20)
        assert len(result) > 1

    def test_chunk_text_empty(self):
        from app.rag.chunker import chunk_text
        assert chunk_text("") == []


class TestSymmetricCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        from app.quantum.symmetric_crypto import SymmetricCryptoService
        secret = b"test_shared_secret_for_kyber"
        plaintext = b"Sensitive alert data: DDoS detected"
        encrypted = SymmetricCryptoService.encrypt(plaintext, secret)
        assert "ciphertext" in encrypted
        assert "nonce" in encrypted
        decrypted = SymmetricCryptoService.decrypt(encrypted["ciphertext"], encrypted["nonce"], secret)
        assert decrypted == plaintext

    def test_derive_key(self):
        from app.quantum.symmetric_crypto import SymmetricCryptoService
        key = SymmetricCryptoService.derive_key(b"secret")
        assert len(key) == 32

    def test_wrong_key_fails(self):
        from app.quantum.symmetric_crypto import SymmetricCryptoService
        from cryptography.exceptions import InvalidTag
        secret = b"correct_secret_key_for_testing"
        wrong = b"wrong_secret_key_for_testing"
        encrypted = SymmetricCryptoService.encrypt(b"data", secret)
        with pytest.raises(InvalidTag):
            SymmetricCryptoService.decrypt(encrypted["ciphertext"], encrypted["nonce"], wrong)


class TestPacketParser:
    def test_parse_non_ip_returns_none(self):
        from app.packet_capture.packet_parser import parse_packet
        result = parse_packet(None, "eth0")
        assert result is None


class TestCaptureService:
    def test_status_without_scapy(self):
        from app.packet_capture.capture_service import CaptureService
        svc = CaptureService()
        status = svc.status()
        assert hasattr(status, "available")
        assert hasattr(status, "running")


class TestDetectionEngine:
    def test_not_available_without_models(self):
        from app.detection.engine.detection_engine import DetectionEngine
        engine = DetectionEngine(model_directory="/tmp/nonexistent_models")
        assert engine.available is False

    def test_detect_without_models_raises(self):
        from app.detection.engine.detection_engine import DetectionEngine
        engine = DetectionEngine(model_directory="/tmp/nonexistent_models")
        with pytest.raises(RuntimeError, match="not trained"):
            engine.detect([0.0] * 52)


class TestDetectionPipeline:
    def test_pipeline_not_running_by_default(self):
        from app.detection.pipeline import DetectionPipeline
        pipeline = DetectionPipeline()
        assert pipeline.running is False
        assert pipeline.detection_count == 0

    def test_pipeline_start_without_models_raises(self):
        from app.detection.pipeline import DetectionPipeline
        pipeline = DetectionPipeline()
        with pytest.raises(RuntimeError, match="not trained"):
            pipeline.start(None)


class TestKyberService:
    def test_unavailable_returns_false(self):
        from app.quantum.kyber_service import KyberService
        svc = KyberService()
        if not svc.available:
            result = svc.keygen()
            assert result.available is False
            assert "pqcrypto" in result.reason

    def test_key_store_isolation(self):
        from app.quantum.kyber_service import KyberService
        svc = KyberService()
        handle = svc._store_key(b"test_key_bytes")
        assert svc._retrieve_key(handle) == b"test_key_bytes"
        assert svc._retrieve_key("nonexistent") is None
        svc._delete_key(handle)
        assert svc._retrieve_key(handle) is None


class TestModelStatus:
    def test_model_status_without_models(self):
        from app.detection.engine.detection_engine import DetectionEngine
        engine = DetectionEngine(model_directory="/tmp/nonexistent_models")
        assert engine.available is False
        assert engine.scaler is None
        assert engine.label_encoder is None
