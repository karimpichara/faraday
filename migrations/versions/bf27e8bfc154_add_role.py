"""add role

Revision ID: bf27e8bfc154
Revises: 23966301910c
Create Date: 2025-08-11 14:58:54.577467

"""

from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = "bf27e8bfc154"
down_revision = "23966301910c"
branch_labels = None
depends_on = None


def upgrade():
    # Create a connection to execute the insert
    connection = op.get_bind()

    # Define the table structure for bulk insert
    roles = sa.table(
        "roles",
        sa.column("name", sa.String),
        sa.column("uuid", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
        sa.column("active", sa.Boolean),
    )

    # Define the data to insert
    now = datetime.now(timezone.utc)
    roles_data = [
        {
            "name": "supervisor",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        }
    ]

    # Insert the data
    connection.execute(roles.insert(), roles_data)


def downgrade():
    # Remove the inserted role
    connection = op.get_bind()

    # Delete the supervisor role
    connection.execute(
        sa.text("DELETE FROM roles WHERE name = :role_name"),
        {"role_name": "supervisor"},
    )
