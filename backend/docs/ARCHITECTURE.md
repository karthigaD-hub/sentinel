# Q-Sentinel Backend

AI-powered network intrusion detection system with post-quantum security.

## Architecture

Q-Sentinel combines deep-learning anomaly detection, supervised attack classification,
SHAP-based explainability, a RAG-powered security assistant, and post-quantum
Kyber768 + AES-256-GCM alert encryption.

### Core Modules

| Module | Purpose |
|--------|---------|
| `app/packet_capture/` | Real-time packet capture via Scapy, flow tracking, interface management |
| `app/detection/features/` | 52-feature CICIDS2017-compatible flow feature extraction |
| `app/detection/training/` | Dataset preparation, PyTorch Autoencoder, XGBoost classifier |
| `app/detection/engine/` | Detection engine combining anomaly + classification + severity |
| `app/explainability/` | SHAP TreeExplainer for XGBoost predictions |
| `app/rag/` | Document chunking, sentence-transformer embeddings, cosine-similarity retrieval |
| `app/llm/` | OpenAI-compatible LLM service + AI security assistant |
| `app/quantum/` | Kyber768 key encapsulation + AES-256-GCM symmetric encryption |
| `app/alerts/` | Alert management + secure alert pipeline with quantum encryption |

### Detection Pipeline

```
Packet Capture (Scapy)
    -> Flow Aggregation (FlowTracker)
    -> Feature Extraction (52 CICIDS2017 features)
    -> Autoencoder (anomaly score vs threshold)
    -> XGBoost (attack classification)
    -> Severity Engine (critical/high/medium/low)
    -> SHAP Explanation (top contributing features)
    -> Secure Alert Pipeline (Kyber768 + AES-256-GCM)
    -> WebSocket broadcast
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL async connection string |
| `SECRET_KEY` | Yes | JWT signing key |
| `LLM_PROVIDER` | No | LLM provider (currently: `openai`) |
| `LLM_MODEL` | No | Model name (e.g. `gpt-4o-mini`) |
| `LLM_API_KEY` | No | API key for the LLM provider |
| `MODEL_DIRECTORY` | No | Directory for trained models (default: `./models`) |
| `QUANTUM_KYBER_VARIANT` | No | Kyber variant (default: `kyber768`) |

### Database Migration

```bash
cd backend
alembic upgrade head
```

## Training Models

### 1. Prepare CICIDS2017 Dataset

Download the CICIDS2017 dataset CSV and run:

```bash
python -m app.detection.training.prepare_dataset \
    --input /path/to/CICIDS2017.csv \
    --output ./models
```

This produces:
- `train.npz`, `val.npz`, `test.npz` — scaled train/val/test splits
- `scaler.joblib` — fitted StandardScaler
- `label_encoder.joblib` — fitted LabelEncoder
- `feature_schema.json` — feature names and label classes

### 2. Train Autoencoder

```python
import numpy as np
from app.detection.training.autoencoder import AutoencoderModel

train = np.load("./models/train.npz")
val = np.load("./models/val.npz")

model = AutoencoderModel(input_dim=52, encoding_dim=16, hidden_dims=[64, 32])
model.train(train["X"], val["X"], epochs=100, batch_size=256)
model.save("./models/autoencoder.pt")
```

### 3. Train XGBoost Classifier

```python
import numpy as np
from app.detection.training.xgboost_model import XGBoostModel

train = np.load("./models/train.npz")
val = np.load("./models/val.npz")

model = XGBoostModel()
model.train(train["X"], train["y"], val["X"], val["y"])
model.save("./models/xgboost.joblib")
```

## API Endpoints

### Capture
- `GET /api/v1/capture/interfaces` — List network interfaces
- `GET /api/v1/capture/status` — Capture status
- `POST /api/v1/capture/start?interface=eth0` — Start capture
- `POST /api/v1/capture/stop` — Stop capture
- `GET /api/v1/capture/statistics` — Flow statistics

### Detection
- `GET /api/v1/detection/status` — Detection engine status
- `GET /api/v1/detection/model/status` — Model availability and version
- `GET /api/v1/detection/model/metrics` — Training metrics (accuracy, F1, confusion matrix)
- `GET /api/v1/detection/results` — Paginated detection history

### Alerts
- `GET /api/v1/alerts` — Paginated alerts
- `GET /api/v1/alerts/{id}` — Alert detail
- `POST /api/v1/alerts/{id}/acknowledge` — Acknowledge alert
- `POST /api/v1/alerts/{id}/resolve` — Resolve alert

### Quantum Security
- `GET /api/v1/quantum/status` — Kyber + AES-GCM availability
- `POST /api/v1/quantum/keygen` — Generate Kyber768 keypair
- `POST /api/v1/quantum/test` — End-to-end Kyber test

### AI Assistant
- `POST /api/v1/assistant/chat` — Chat with RAG-powered security assistant
- `GET /api/v1/assistant/history` — Conversation history

### RAG / Threat Intel
- `POST /api/v1/rag/search` — Semantic search over threat intel
- `POST /api/v1/rag/query` — RAG query (retrieval + LLM answer)
- `GET /api/v1/threat-intel` — Threat intel status

## Testing

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Feature Schema

52 features compatible with CICIDS2017:

Duration, protocol number, forward/backward packet counts and lengths,
inter-arrival time statistics, flow bytes/packets per second, flag counts
(SYN/ACK/FIN/RST/PSH/URG), active/idle time statistics, and more.

## Security

- JWT access + refresh tokens with Argon2 password hashing
- Role-based access control (admin, analyst, viewer)
- Post-quantum Kyber768 key establishment for alert encryption
- AES-256-GCM authenticated encryption for alert payloads
- RLS-ready database models
