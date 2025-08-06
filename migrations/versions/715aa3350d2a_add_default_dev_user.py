"""add default dev user

Revision ID: 715aa3350d2a
Revises: 167c1dec139a
Create Date: 2025-08-06 16:49:48.272717

"""

from alembic import op
from sqlalchemy import text
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash


# revision identifiers, used by Alembic.
revision = "715aa3350d2a"
down_revision = "167c1dec139a"
branch_labels = None
depends_on = None


def upgrade():
    """Create default dev user with admin role."""
    # Get database connection
    conn = op.get_bind()

    # Check if admin role exists, create if not
    result = conn.execute(text("SELECT id FROM roles WHERE name = 'admin'")).fetchone()
    if not result:
        # Create admin role
        role_uuid = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)
        conn.execute(
            text(
                """
            INSERT INTO roles (uuid, created_at, updated_at, active, name)
            VALUES (:uuid, :created_at, :updated_at, :active, :name)
        """
            ),
            {
                "uuid": role_uuid,
                "created_at": current_time,
                "updated_at": current_time,
                "active": True,
                "name": "admin",
            },
        )
        role_id = conn.execute(
            text("SELECT id FROM roles WHERE uuid = :uuid"), {"uuid": role_uuid}
        ).fetchone()[0]
    else:
        role_id = result[0]

    # Check if dev user exists, create if not
    result = conn.execute(
        text("SELECT id FROM users WHERE username = 'dev'")
    ).fetchone()
    if not result:
        # Create dev user
        user_uuid = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)
        hashed_password = generate_password_hash("devSbip.37")

        conn.execute(
            text(
                """
            INSERT INTO users (uuid, created_at, updated_at, active, username, password)
            VALUES (:uuid, :created_at, :updated_at, :active, :username, :password)
        """
            ),
            {
                "uuid": user_uuid,
                "created_at": current_time,
                "updated_at": current_time,
                "active": True,
                "username": "dev",
                "password": hashed_password,
            },
        )
        user_id = conn.execute(
            text("SELECT id FROM users WHERE uuid = :uuid"), {"uuid": user_uuid}
        ).fetchone()[0]

        # Assign admin role to dev user
        user_role_uuid = str(uuid.uuid4())
        conn.execute(
            text(
                """
            INSERT INTO user_roles (uuid, created_at, updated_at, active, user_id, role_id)
            VALUES (:uuid, :created_at, :updated_at, :active, :user_id, :role_id)
        """
            ),
            {
                "uuid": user_role_uuid,
                "created_at": current_time,
                "updated_at": current_time,
                "active": True,
                "user_id": user_id,
                "role_id": role_id,
            },
        )


def downgrade():
    """Remove default dev user and admin role if no other users have it."""
    conn = op.get_bind()

    # Get dev user ID
    result = conn.execute(
        text("SELECT id FROM users WHERE username = 'dev'")
    ).fetchone()
    if result:
        user_id = result[0]

        # Remove user role assignments
        conn.execute(
            text("DELETE FROM user_roles WHERE user_id = :user_id"),
            {"user_id": user_id},
        )

        # Remove dev user
        conn.execute(
            text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id}
        )

    # Check if admin role is still used by other users
    result = conn.execute(
        text(
            """
        SELECT COUNT(*) FROM user_roles ur 
        JOIN roles r ON ur.role_id = r.id 
        WHERE r.name = 'admin'
    """
        )
    ).fetchone()

    if result and result[0] == 0:
        # No other users have admin role, safe to delete
        conn.execute(text("DELETE FROM roles WHERE name = 'admin'"))
