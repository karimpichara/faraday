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
        Create multiple ordenes de trabajo using efficient ON CONFLICT DO NOTHING.

        Returns:
            Dictionary with detailed results including which codes were inserted, not_inserted, and had errors
        """
        if not ordenes_data:
            return {
                "inserted": [],
                "not_inserted": [],
                "errors": [],
                "inserted_count": 0,
                "total_count": 0,
                "skipped_count": 0,
            }

        # Prepare data for bulk insert with conflict handling
        import uuid
        from datetime import datetime

        insert_data = []
        all_codigos = []

        for orden_data in ordenes_data:
            codigo = orden_data["codigo"]
            all_codigos.append(codigo)

            # Add BaseModel fields with defaults
            insert_data.append(
                {
                    "codigo": codigo,
                    "id_empresa": orden_data["id_empresa"],
                    "uuid": str(uuid.uuid4()),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "active": True,
                }
            )

        try:
            # Use PostgreSQL's INSERT ... ON CONFLICT DO NOTHING with RETURNING
            stmt = insert(OrdenTrabajo).values(insert_data)
            stmt = stmt.on_conflict_do_nothing(index_elements=["codigo"])
            stmt = stmt.returning(OrdenTrabajo.codigo)

            result = db.session.execute(stmt)
            db.session.commit()

            # Get the codes that were actually inserted
            inserted_codes = [row[0] for row in result.fetchall()]

            # Calculate not_inserted (codes that existed and were skipped)
            not_inserted_codes = [
                codigo for codigo in all_codigos if codigo not in inserted_codes
            ]

            return {
                "inserted": inserted_codes,
                "not_inserted": not_inserted_codes,
                "errors": [],  # No errors if we reach here
                "inserted_count": len(inserted_codes),
                "total_count": len(ordenes_data),
                "skipped_count": len(not_inserted_codes),
                "error_count": 0,
            }

        except Exception:
            db.session.rollback()
            # If there's a database error, all codes go to errors
            return {
                "inserted": [],
                "not_inserted": [],
                "errors": all_codigos,
                "inserted_count": 0,
                "total_count": len(ordenes_data),
                "skipped_count": 0,
                "error_count": len(all_codigos),
            }

    def get_orden_trabajo_by_codigo(self, codigo: str) -> OrdenTrabajo | None:
        """Get orden de trabajo by codigo"""
        return OrdenTrabajo.query.filter_by(codigo=codigo).first()

    def get_ordenes_trabajo_all(self) -> list[OrdenTrabajo]:
        """Get all ordenes de trabajo"""
        return OrdenTrabajo.query.all()

    def get_ordenes_trabajo_by_user_empresas(
        self,
        user_empresa_ids: list[int],
        page: int = 1,
        per_page: int = 20,
        search_codigo: str = None,
        search_fecha_inicio: str = None,
        search_fecha_fin: str = None,
    ) -> dict[str, Any]:
        """
        Get ordenes de trabajo with pagination and search filters for user's empresas.

        Args:
            user_empresa_ids: List of empresa IDs the user has access to
            page: Page number (1-indexed)
            per_page: Number of records per page (max 20)
            search_codigo: Optional codigo filter
            search_fecha_inicio: Optional start date filter (YYYY-MM-DD)
            search_fecha_fin: Optional end date filter (YYYY-MM-DD)

        Returns:
            Dictionary with paginated results and metadata
        """
        from datetime import datetime

        # Ensure per_page doesn't exceed maximum
        per_page = min(per_page, 20)

        # Base query filtered by user's empresas
        query = OrdenTrabajo.active_records().filter(
            OrdenTrabajo.id_empresa.in_(user_empresa_ids)
        )

        # Apply search filters
        if search_codigo:
            query = query.filter(OrdenTrabajo.codigo.ilike(f"%{search_codigo}%"))

        if search_fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(search_fecha_inicio, "%Y-%m-%d")
                query = query.filter(OrdenTrabajo.created_at >= fecha_inicio)
            except ValueError:
                pass  # Invalid date format, ignore filter

        if search_fecha_fin:
            try:
                fecha_fin = datetime.strptime(search_fecha_fin, "%Y-%m-%d")
                # Add one day to include the entire end date
                from datetime import timedelta

                fecha_fin = fecha_fin + timedelta(days=1)
                query = query.filter(OrdenTrabajo.created_at < fecha_fin)
            except ValueError:
                pass  # Invalid date format, ignore filter

        # Order by most recent first
        query = query.order_by(OrdenTrabajo.created_at.desc())

        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "ordenes": pagination.items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_prev": pagination.has_prev,
                "has_next": pagination.has_next,
                "prev_num": pagination.prev_num,
                "next_num": pagination.next_num,
            },
            "search_filters": {
                "codigo": search_codigo,
                "fecha_inicio": search_fecha_inicio,
                "fecha_fin": search_fecha_fin,
            },
        }
