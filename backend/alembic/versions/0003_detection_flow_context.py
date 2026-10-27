"""add flow context and severity to detections

Revision ID: 0003_detection_flow_context
Revises: 0002_consolidate_roles
Create Date: 2026-10-27

Adds flow context columns (source_ip, destination_ip, protocol, source_port,
destination_port) and severity + classification columns to the detections
table so users can see exactly which traffic flow triggered each detection.
All new columns are nullable so existing rows remain valid.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_detection_flow_context"
down_revision = "0002_consolidate_roles"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("detections", sa.Column("source_ip", sa.String(255), nullable=True))
    op.add_column("detections", sa.Column("destination_ip", sa.String(255), nullable=True))
    op.add_column("detections", sa.Column("protocol", sa.String(30), nullable=True))
    op.add_column("detections", sa.Column("source_port", sa.Integer(), nullable=True))
    op.add_column("detections", sa.Column("destination_port", sa.Integer(), nullable=True))
    op.add_column("detections", sa.Column("severity", sa.String(30), nullable=True))
    op.add_column("detections", sa.Column("classification", sa.String(50), nullable=True))
    op.add_column("detections", sa.Column("anomaly_score", sa.Float(), nullable=True))
    op.create_index("ix_detections_label", "detections", ["label"])
    op.create_index("ix_detections_severity", "detections", ["severity"])

def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is intentionally unsupported")
