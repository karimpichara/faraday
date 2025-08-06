"""add auth tables manually

Revision ID: 167c1dec139a
Revises: 1646c6b19bbe
Create Date: 2025-08-06 16:31:43.478373

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "167c1dec139a"
down_revision = "1646c6b19bbe"
branch_labels = None
depends_on = None


def upgrade():
    # Create roles table
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_roles_active"), "roles", ["active"], unique=False)

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password", sa.String(length=256), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(op.f("ix_users_active"), "users", ["active"], unique=False)

    # Create user_roles table
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(
        op.f("ix_user_roles_active"), "user_roles", ["active"], unique=False
    )


def downgrade():
    # Drop tables in reverse order (because of foreign keys)
    op.drop_index(op.f("ix_user_roles_active"), table_name="user_roles")
    op.drop_table("user_roles")

    op.drop_index(op.f("ix_users_active"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_roles_active"), table_name="roles")
    op.drop_table("roles")
