"""add_initial_empresas_externas_data

Revision ID: bfcbecca0b16
Revises: 12e4f5bc0229
Create Date: 2025-08-07 18:28:29.431597

"""

from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = "bfcbecca0b16"
down_revision = "12e4f5bc0229"
branch_labels = None
depends_on = None


def upgrade():
    # Create a connection to execute the insert
    connection = op.get_bind()

    # Define the table structure for bulk insert
    empresas_externas_toa = sa.table(
        "empresas_externas_toa",
        sa.column("nombre", sa.String),
        sa.column("nombre_toa", sa.String),
        sa.column("rut", sa.String),
        sa.column("uuid", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
        sa.column("active", sa.Boolean),
    )

    # Define the data to insert
    now = datetime.now(timezone.utc)
    empresas_data = [
        {
            "nombre": "Creaciones Tecnologicas SpA",
            "nombre_toa": "CREA",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
        {
            "nombre": "Instal",
            "nombre_toa": "INTA",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
        {
            "nombre": "Atlantis",
            "nombre_toa": "ATLA",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
        {
            "nombre": "Beginning",
            "nombre_toa": "BEGI",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
        {
            "nombre": "xr3",
            "nombre_toa": "XR3",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
        {
            "nombre": "palo tinto",
            "nombre_toa": "PATI",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
        {
            "nombre": "Hyz",
            "nombre_toa": "HYZ",
            "rut": "70000000-0",
            "uuid": str(uuid.uuid4()),
            "created_at": now,
            "updated_at": now,
            "active": True,
        },
    ]

    # Insert the data
    connection.execute(empresas_externas_toa.insert(), empresas_data)


def downgrade():
    # Remove the inserted data
    connection = op.get_bind()

    # Define the specific nombre_toa values to delete
    nombres_toa_to_delete = ["CREA", "INTA", "ATLA", "BEGI", "XR3", "PATI", "HYZ"]

    # Delete the records
    connection.execute(
        sa.text("DELETE FROM empresas_externas_toa WHERE nombre_toa IN :nombres_toa"),
        {"nombres_toa": tuple(nombres_toa_to_delete)},
    )
