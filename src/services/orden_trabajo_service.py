from typing import Any

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
    ) -> list[OrdenTrabajo]:
        """Create multiple ordenes de trabajo in bulk"""
        ordenes = []
        for orden_data in ordenes_data:
            orden = OrdenTrabajo(
                codigo=orden_data["codigo"], id_empresa=orden_data["id_empresa"]
            )
            ordenes.append(orden)

        db.session.add_all(ordenes)
        db.session.commit()
        return ordenes

    def get_orden_trabajo_by_codigo(self, codigo: str) -> OrdenTrabajo | None:
        """Get orden de trabajo by codigo"""
        return OrdenTrabajo.query.filter_by(codigo=codigo).first()

    def get_ordenes_trabajo_all(self) -> list[OrdenTrabajo]:
        """Get all ordenes de trabajo"""
        return OrdenTrabajo.query.all()
