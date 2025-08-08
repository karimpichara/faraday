from typing import Any

from src.services.empresas_externas_service import EmpresasExternasService
from src.services.orden_trabajo_service import OrdenTrabajoService


class OrdenTrabajoUseCase:
    def __init__(
        self,
        orden_trabajo_service: OrdenTrabajoService,
        empresas_externas_service: EmpresasExternasService,
    ):
        self.orden_trabajo_service = orden_trabajo_service
        self.empresas_externas_service = empresas_externas_service

    def validate_empresa_exists(self, id_empresa: int) -> bool:
        """
        Validate that the empresa exists in the database.

        Args:
            id_empresa: The empresa ID to validate

        Returns:
            True if empresa exists, False otherwise
        """
        try:
            empresas = self.empresas_externas_service.get_empresas_externas_toa_all()
            empresa_ids = [
                empresa.id for empresa in empresas
            ]  # Fixed: use .id instead of ["id"]
            return id_empresa in empresa_ids
        except Exception:
            return False

    def add_ordenes_trabajo(self, ordenes_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Add multiple ordenes de trabajo to the database.

        Args:
            ordenes_data: List of dictionaries with id_empresa and codigo

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If data validation fails
        """

        # Validate input data structure
        if not isinstance(ordenes_data, list):
            raise ValueError("Los datos de entrada deben ser una lista")

        if not ordenes_data:
            raise ValueError("Los datos de entrada no pueden estar vacíos")

        # Validate each orden data
        validated_ordenes = []
        errors = []

        for i, orden_data in enumerate(ordenes_data):
            if not isinstance(orden_data, dict):
                errors.append(f"Elemento {i}: Debe ser un diccionario")
                continue

            if "id_empresa" not in orden_data or "codigo" not in orden_data:
                errors.append(
                    f"Elemento {i}: Debe contener los campos 'id_empresa' y 'codigo'"
                )
                continue

            try:
                id_empresa = int(orden_data["id_empresa"])
                codigo = str(orden_data["codigo"]).strip()
            except (ValueError, TypeError):
                errors.append(f"Elemento {i}: Tipos de datos inválidos")
                continue

            if not codigo:
                errors.append(f"Elemento {i}: El 'codigo' no puede estar vacío")
                continue

            # Validate empresa exists
            if not self.validate_empresa_exists(id_empresa):
                errors.append(f"Elemento {i}: La empresa con id {id_empresa} no existe")
                continue

            # Check if orden already exists
            existing_orden = self.orden_trabajo_service.get_orden_trabajo_by_codigo(
                codigo
            )
            if existing_orden:
                errors.append(f"Elemento {i}: La orden con código '{codigo}' ya existe")
                continue

            validated_ordenes.append({"id_empresa": id_empresa, "codigo": codigo})

        # If there are validation errors, raise exception
        if errors:
            raise ValueError(f"Errores de validación: {'; '.join(errors)}")

        # Create ordenes de trabajo in bulk (with conflict handling)
        try:
            result = self.orden_trabajo_service.create_ordenes_trabajo_bulk(
                validated_ordenes
            )

            # Prepare response message
            message_parts = []
            if result["inserted_count"] > 0:
                message_parts.append(
                    f"Se insertaron {result['inserted_count']} órdenes nuevas"
                )
            if result["skipped_count"] > 0:
                message_parts.append(
                    f"Se omitieron {result['skipped_count']} órdenes existentes"
                )

            message = (
                ". ".join(message_parts)
                if message_parts
                else "No se procesaron órdenes"
            )

            return {
                "success": True,
                "message": message,
                "inserted_count": result["inserted_count"],
                "skipped_count": result["skipped_count"],
                "total_processed": result["total_count"],
                "validation_errors": errors if errors else None,
            }

        except Exception as e:
            raise RuntimeError(f"Error de base de datos: {str(e)}") from e
