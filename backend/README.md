# Q-Sentinel Backend

Q-Sentinel is a FastAPI backend foundation for an AI-assisted cyber defense system. It intentionally does not fabricate traffic, detections, threat intelligence, explanations, or assistant answers. Features that need local permissions, trained models, external providers, or worker infrastructure return an explicit unavailable response until configured.

## Requirements

- Python 3.12
- PostgreSQL 16+
- Redis 7+
- Operating-system permission for packet capture when capture is enabled

## Setup

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env  # Windows
cp .env.example .env   # Linux/macOS
```

Set real values in `.env`, especially `DATABASE_URL` and `SECRET_KEY`. Never commit `.env`.

## Database and workers

Start PostgreSQL and Redis, then apply the schema with Alembic:

```bash
alembic upgrade head
celery -A app.tasks.celery_app worker --loglevel=info
```

Run the API from the `backend` directory:

```bash
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```

The tests require a configured test database for integration coverage. Packet capture requires an approved interface and elevated capture privileges on Linux or Npcap permissions on Windows. Model inference requires files in `MODEL_DIRECTORY`; RAG and assistant features require configured data and an external LLM provider.

## Security

Access tokens are short-lived JWTs. Refresh tokens are high-entropy opaque values stored only as SHA-256 hashes and rotated with family reuse detection. Passwords use Argon2id. Production deployments should use TLS, restrictive CORS and trusted hosts, a strong secret, a managed database, and least-privilege operating-system permissions.
