"""persistent RAG index: rag_chunks table and document content hash

Revision ID: 0004_rag_persistent_index
Revises: 0003_detection_flow_context
Create Date: 2026-11-10

Plain-English summary
---------------------
Threat-intelligence passages and their search vectors were previously kept
only in server memory, so every restart emptied the knowledge index. This
migration stores each passage ("chunk") and its vector in the database.

1. New table `rag_chunks`
   - One row per passage, linked to its parent document in `rag_documents`.
   - Stores the passage text, a hash of the text (used for duplicate removal),
     the embedding vector, and the name of the embedding model used.
   - Deleting a document deletes its chunks (ON DELETE CASCADE).
2. Modified table `rag_documents`
   - New nullable column `content_hash` (SHA-256 of the full document text)
     so re-ingesting an unchanged document is detected and skipped.

Security
--------
- Row level security is enabled on `rag_chunks` with no policies, and the
  public API roles (anon, authenticated) lose all privileges on it. Only the
  backend server, which connects with its own database credentials, can read
  or write this table.

Notes
-----
- Idempotent: migration 0001 builds tables from the current models, so on a
  fresh database both the table and column already exist and are skipped.
- No data is deleted or altered by this migration.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_rag_persistent_index"
down_revision = "0003_detection_flow_context"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "rag_documents" in tables:
        document_columns = {column["name"] for column in inspector.get_columns("rag_documents")}
        if "content_hash" not in document_columns:
            op.add_column("rag_documents", sa.Column("content_hash", sa.String(64), nullable=True))

    if "rag_chunks" not in tables:
        op.create_table(
            "rag_chunks",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rag_documents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("chunk_index", sa.Integer(), nullable=False),
            sa.Column("source", sa.String(200), nullable=False),
            sa.Column("external_id", sa.String(200), nullable=False),
            sa.Column("text", sa.Text(), nullable=False),
            sa.Column("text_hash", sa.String(64), nullable=False),
            sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=False),
            sa.Column("embedding_model", sa.String(200), nullable=False),
            sa.Column("metadata_json", sa.JSON(), nullable=True),
            sa.UniqueConstraint("document_id", "chunk_index", name="uq_rag_chunks_document_index"),
        )
        op.create_index("ix_rag_chunks_document_id", "rag_chunks", ["document_id"])
        op.create_index("ix_rag_chunks_text_hash", "rag_chunks", ["text_hash"])

    op.execute("ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY")
    for role in ("anon", "authenticated"):
        role_exists = bind.execute(sa.text("SELECT 1 FROM pg_roles WHERE rolname = :role"), {"role": role}).first()
        if role_exists:
            op.execute(f'REVOKE ALL ON rag_chunks FROM "{role}"')


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is intentionally unsupported")
