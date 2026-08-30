"""initial schema"""
from alembic import op
from app.models import Base
from sqlalchemy import create_engine
from app.core.config import settings

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)

def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is intentionally unsupported")
