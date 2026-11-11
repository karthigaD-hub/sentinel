"""add flow context and severity to detections

Revision ID: 0003_detection_flow_context
Revises: 0002_consolidate_roles
Create Date: 2026-10-27

Adds flow context columns (source_ip, destination_ip, protocol, source_port,
destination_port) and severity + classification columns to the detections
table so users can see exactly which traffic flow triggered each detection.
All new columns are nullable so existing rows remain valid.

Idempotent: migration 0001 builds tables from the current models, so on a
fresh database these columns already exist and are skipped.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_detection_flow_context"
down_revision = "0002_consolidate_roles"
branch_labels = None
depends_on = None

NEW_COLUMNS = [
    sa.Column("source_ip", sa.String(255), nullable=True),
    sa.Column("destination_ip", sa.String(255), nullable=True),
    sa.Column("protocol", sa.String(30), nullable=True),
    sa.Column("source_port", sa.Integer(), nullable=True),
    sa.Column("destination_port", sa.Integer(), nullable=True),
    sa.Column("severity", sa.String(30), nullable=True),
    sa.Column("classification", sa.String(50), nullable=True),
    sa.Column("anomaly_score", sa.Float(), nullable=True),
]
NEW_INDEXES = {"ix_detections_label": ["label"], "ix_detections_severity": ["severity"]}

def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    existing_columns = {column["name"] for column in inspector.get_columns("detections")}
    for column in NEW_COLUMNS:
        if column.name not in existing_columns:
            op.add_column("detections", column)

    existing_indexes = {index["name"] for index in inspector.get_indexes("detections")}
    for index_name, columns in NEW_INDEXES.items():
        if index_name not in existing_indexes:
            op.create_index(index_name, "detections", columns)

def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is intentionally unsupported")
