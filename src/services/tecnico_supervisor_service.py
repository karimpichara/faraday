from typing import Any

from src.models import db
from src.models.tecnico_supervisor import TecnicoSupervisor


class TecnicoSupervisorService:
    """Service for managing TecnicoSupervisor database operations."""

    def create_tecnico_supervisor(
        self,
        nombre_tecnico: str,
        rut_tecnico: str,
        nombre_supervisor: str,
        id_empresa: int,
    ) -> TecnicoSupervisor:
        """
        Create a new tecnico supervisor record.

        Args:
            nombre_tecnico: Name of the technician
            rut_tecnico: RUT of the technician
            nombre_supervisor: Name of the supervisor
            id_empresa: ID of the empresa

        Returns:
            Created TecnicoSupervisor instance

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            tecnico_supervisor = TecnicoSupervisor(
                nombre_tecnico=nombre_tecnico.strip(),
                rut_tecnico=rut_tecnico.strip(),
                nombre_supervisor=nombre_supervisor.strip(),
                id_empresa=id_empresa,
            )

            db.session.add(tecnico_supervisor)
            db.session.commit()

            return tecnico_supervisor

        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al crear el técnico supervisor: {str(e)}") from e

    def create_tecnicos_supervisores_bulk(
        self, tecnicos_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Create multiple tecnico supervisor records in bulk.

        Args:
            tecnicos_data: List of dictionaries with tecnico data

        Returns:
            Dictionary with operation results

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            created_count = 0
            created_ids = []

            for data in tecnicos_data:
                tecnico_supervisor = TecnicoSupervisor(
                    nombre_tecnico=data["nombre_tecnico"].strip(),
                    rut_tecnico=data["rut_tecnico"].strip(),
                    nombre_supervisor=data["nombre_supervisor"].strip(),
                    id_empresa=data["id_empresa"],
                )

                db.session.add(tecnico_supervisor)
                db.session.flush()  # Get the ID without committing
                created_ids.append(tecnico_supervisor.id)
                created_count += 1

            db.session.commit()

            return {
                "created_count": created_count,
                "created_ids": created_ids,
                "total_count": len(tecnicos_data),
            }

        except Exception as e:
            db.session.rollback()
            raise RuntimeError(
                f"Error al crear los técnicos supervisores: {str(e)}"
            ) from e

    def get_tecnicos_by_empresa(self, id_empresa: int) -> list[TecnicoSupervisor]:
        """
        Get all tecnicos for a specific empresa.

        Args:
            id_empresa: ID of the empresa

        Returns:
            List of TecnicoSupervisor instances
        """
        return TecnicoSupervisor.active_records().filter_by(id_empresa=id_empresa).all()

    def get_tecnico_by_id(self, tecnico_id: int) -> TecnicoSupervisor | None:
        """
        Get a tecnico by ID.

        Args:
            tecnico_id: ID of the tecnico

        Returns:
            TecnicoSupervisor instance or None if not found
        """
        return TecnicoSupervisor.active_records().filter_by(id=tecnico_id).first()

    def get_all_tecnicos_supervisores(self) -> list[TecnicoSupervisor]:
        """
        Get all active tecnicos supervisores from all empresas.

        Returns:
            List of all active TecnicoSupervisor instances
        """
        return TecnicoSupervisor.active_records().all()
