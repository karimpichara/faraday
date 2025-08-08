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
            raise ValueError("Input data must be a list")

        if not ordenes_data:
            raise ValueError("Input data cannot be empty")

        # Validate each orden data
        validated_ordenes = []
        errors = []

        for i, orden_data in enumerate(ordenes_data):
            if not isinstance(orden_data, dict):
                errors.append(f"Item {i}: Must be a dictionary")
                continue

            if "id_empresa" not in orden_data or "codigo" not in orden_data:
                errors.append(
                    f"Item {i}: Must contain 'id_empresa' and 'codigo' fields"
                )
                continue

            try:
                id_empresa = int(orden_data["id_empresa"])
                codigo = str(orden_data["codigo"]).strip()
            except (ValueError, TypeError):
                errors.append(f"Item {i}: Invalid data types")
                continue

            if not codigo:
                errors.append(f"Item {i}: 'codigo' cannot be empty")
                continue

            # Validate empresa exists
            if not self.validate_empresa_exists(id_empresa):
                errors.append(f"Item {i}: Empresa with id {id_empresa} does not exist")
                continue

            # Check if orden already exists
            existing_orden = self.orden_trabajo_service.get_orden_trabajo_by_codigo(
                codigo
            )
            if existing_orden:
                errors.append(f"Item {i}: Orden with codigo '{codigo}' already exists")
                continue

            validated_ordenes.append({"id_empresa": id_empresa, "codigo": codigo})

        # If there are validation errors, raise exception
        if errors:
            raise ValueError(f"Validation errors: {'; '.join(errors)}")

        # Create ordenes de trabajo in bulk
        try:
            created_ordenes = self.orden_trabajo_service.create_ordenes_trabajo_bulk(
                validated_ordenes
            )

            return {
                "message": "Ordenes de trabajo created successfully",
                "created_count": len(created_ordenes),
                "ordenes": [
                    {
                        "id": orden.id,
                        "codigo": orden.codigo,
                        "id_empresa": orden.id_empresa,
                        "created_at": orden.created_at.isoformat(),
                    }
                    for orden in created_ordenes
                ],
            }
        except Exception as e:
            raise RuntimeError(f"Error creating ordenes de trabajo: {str(e)}")
