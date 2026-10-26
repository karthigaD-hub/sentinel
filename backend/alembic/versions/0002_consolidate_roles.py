"""consolidate roles to single user role

Revision ID: 0002_consolidate_roles
Revises: 0001_initial
Create Date: 2026-10-26

Migrates the multi-role RBAC system (admin, analyst, viewer) to a single
unified "user" role. All existing users are reassigned to "user".
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_consolidate_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

USER_PERMISSIONS = [
    "dashboard:view", "capture:view", "capture:start", "capture:stop",
    "detection:view", "alerts:view", "alerts:update", "threatintel:view",
    "assistant:use", "reports:view", "quantum:view", "settings:view", "settings:update",
]

def upgrade() -> None:
    bind = op.get_bind()

    # Create the "user" role if it doesn't exist
    result = bind.execute(sa.text("SELECT id FROM roles WHERE name = 'user'")).fetchone()
    if not result:
        bind.execute(sa.text(
            "INSERT INTO roles (id, name, permissions, created_at, updated_at) "
            "VALUES (gen_random_uuid(), 'user', :permissions, now(), now())"
        ), {"permissions": sa.JSON().bind_processor(bind.dialect)(USER_PERMISSIONS)})

    # Reassign all users to the "user" role
    bind.execute(sa.text(
        "UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'user'), updated_at = now() "
        "WHERE role_id IN (SELECT id FROM roles WHERE name IN ('admin', 'analyst', 'viewer'))"
    ))

    # Delete old roles
    bind.execute(sa.text("DELETE FROM roles WHERE name IN ('admin', 'analyst', 'viewer')"))

def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is intentionally unsupported")
