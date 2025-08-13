"""fix_timezone_existing_data

Revision ID: 2a2cc1ab9823
Revises: bf27e8bfc154
Create Date: 2025-08-13 22:04:54.499509

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a2cc1ab9823"
down_revision = "bf27e8bfc154"
branch_labels = None
depends_on = None


def upgrade():
    """
    Fix existing timezone data: Convert UTC timestamps to Santiago timezone.

    The problem: Existing records were stored as UTC timestamps (naive),
    but now the database timezone is set to America/Santiago.
    PostgreSQL interprets naive timestamps as local time (Santiago),
    so UTC timestamps appear 3-4 hours ahead.

    Solution: Convert existing UTC timestamps to Santiago time by subtracting the offset.
    """

    # Get all tables that have timestamp columns (BaseModel tables)
    tables_to_fix = [
        "users",
        "roles",
        "user_roles",
        "user_empresas",
        "empresas_externas_toa",
        "ordenes_trabajo",
        "comentarios",
        "historia_ot_empresas",
        "tecnicos_supervisores",
    ]

    for table_name in tables_to_fix:
        # Check if table exists before trying to update it
        op.execute(
            f"""
            DO $$ 
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}') THEN
                    -- Convert created_at from UTC to Santiago time
                    -- Santiago is UTC-3 (summer) or UTC-4 (winter), so subtract 3-4 hours
                    UPDATE {table_name} 
                    SET created_at = created_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Santiago'
                    WHERE created_at IS NOT NULL;
                    
                    -- Convert updated_at from UTC to Santiago time (if column exists)
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = '{table_name}' AND column_name = 'updated_at') THEN
                        UPDATE {table_name} 
                        SET updated_at = updated_at AT TIME ZONE 'UTC' AT TIME ZONE 'America/Santiago'
                        WHERE updated_at IS NOT NULL;
                    END IF;
                    
                    RAISE NOTICE 'Fixed timezone for table: {table_name}';
                ELSE
                    RAISE NOTICE 'Table {table_name} does not exist, skipping...';
                END IF;
            END $$;
        """
        )


def downgrade():
    """
    Revert timezone fix: Convert Santiago timestamps back to UTC.
    """

    # Get all tables that have timestamp columns (BaseModel tables)
    tables_to_revert = [
        "users",
        "roles",
        "user_roles",
        "user_empresas",
        "empresas_externas_toa",
        "ordenes_trabajo",
        "comentarios",
        "historia_ot_empresas",
        "tecnicos_supervisores",
    ]

    for table_name in tables_to_revert:
        # Check if table exists before trying to update it
        op.execute(
            f"""
            DO $$ 
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}') THEN
                    -- Convert created_at from Santiago time back to UTC
                    UPDATE {table_name} 
                    SET created_at = created_at AT TIME ZONE 'America/Santiago' AT TIME ZONE 'UTC'
                    WHERE created_at IS NOT NULL;
                    
                    -- Convert updated_at from Santiago time back to UTC (if column exists)
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name = '{table_name}' AND column_name = 'updated_at') THEN
                        UPDATE {table_name} 
                        SET updated_at = updated_at AT TIME ZONE 'America/Santiago' AT TIME ZONE 'UTC'
                        WHERE updated_at IS NOT NULL;
                    END IF;
                    
                    RAISE NOTICE 'Reverted timezone for table: {table_name}';
                ELSE
                    RAISE NOTICE 'Table {table_name} does not exist, skipping...';
                END IF;
            END $$;
        """
        )
