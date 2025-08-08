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
        validation_errors = []

        for i, orden_data in enumerate(ordenes_data):
            if not isinstance(orden_data, dict):
                validation_errors.append(f"item-{i}")
                continue

            if "id_empresa" not in orden_data or "codigo" not in orden_data:
                validation_errors.append(f"item-{i}")
                continue

            try:
                id_empresa = int(orden_data["id_empresa"])
                codigo = str(orden_data["codigo"]).strip()
            except (ValueError, TypeError):
                validation_errors.append(f"item-{i}")
                continue

            if not codigo:
                validation_errors.append(f"item-{i}")
                continue

            if len(codigo) > 32:
                validation_errors.append(codigo)
                continue

            # Validate empresa exists
            if not self.validate_empresa_exists(id_empresa):
                validation_errors.append(codigo)
                continue

            # Note: We don't check for existing ordenes here anymore -
            # the service layer will handle that and report them as "not_inserted"
            validated_ordenes.append({"id_empresa": id_empresa, "codigo": codigo})

        # Create ordenes de trabajo with detailed tracking
        try:
            result = self.orden_trabajo_service.create_ordenes_trabajo_bulk(
                validated_ordenes
            )

            # Combine validation errors with database errors
            all_errors = validation_errors + result["errors"]

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
            if len(all_errors) > 0:
                message_parts.append(
                    f"Se encontraron {len(all_errors)} errores"
                )

            message = (
                ". ".join(message_parts)
                if message_parts
                else "No se procesaron órdenes"
            )

            return {
                "success": True,
                "message": message,
                "inserted": result["inserted"],
                "not_inserted": result["not_inserted"],
                "errors": all_errors,
            }

        except Exception as e:
            raise RuntimeError(f"Error de base de datos: {str(e)}") from e
