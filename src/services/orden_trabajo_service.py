from typing import Any

from sqlalchemy.dialects.postgresql import insert

from src.models import db
from src.models.orden_trabajo import OrdenTrabajo


class OrdenTrabajoService:
    def create_orden_trabajo(self, codigo: str, id_empresa: int) -> OrdenTrabajo:
        """Create a new orden de trabajo"""
        orden_trabajo = OrdenTrabajo(codigo=codigo, id_empresa=id_empresa)
        db.session.add(orden_trabajo)
        db.session.commit()
        return orden_trabajo

    def create_ordenes_trabajo_bulk(
        self, ordenes_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Create multiple ordenes de trabajo in bulk using ON CONFLICT DO NOTHING.

        Returns:
            Dictionary with operation results including inserted count
        """
        if not ordenes_data:
            return {"inserted_count": 0, "total_count": 0, "skipped_count": 0}

        # Prepare data for bulk insert with conflict handling
        import uuid
        from datetime import datetime, timezone

        insert_data = []
        for orden_data in ordenes_data:
            # Add BaseModel fields with defaults
            insert_data.append(
                {
                    "codigo": orden_data["codigo"],
                    "id_empresa": orden_data["id_empresa"],
                    "uuid": str(uuid.uuid4()),
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "active": True,
                }
            )

        # Use PostgreSQL's INSERT ... ON CONFLICT DO NOTHING
        stmt = insert(OrdenTrabajo).values(insert_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["codigo"])

        result = db.session.execute(stmt)
        db.session.commit()

        # Calculate results
        total_count = len(ordenes_data)
        inserted_count = result.rowcount
        skipped_count = total_count - inserted_count

        return {
            "inserted_count": inserted_count,
            "total_count": total_count,
            "skipped_count": skipped_count,
        }

    def get_orden_trabajo_by_codigo(self, codigo: str) -> OrdenTrabajo | None:
        """Get orden de trabajo by codigo"""
        return OrdenTrabajo.query.filter_by(codigo=codigo).first()

    def get_ordenes_trabajo_all(self) -> list[OrdenTrabajo]:
        """Get all ordenes de trabajo"""
        return OrdenTrabajo.query.all()
