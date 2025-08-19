from typing import Any

from src.models.auth.user import User
from src.services.tecnico_supervisor_service import TecnicoSupervisorService


class TecnicoSupervisorUseCase:
    """Use case for managing tecnico supervisor operations."""

    def __init__(self, tecnico_supervisor_service: TecnicoSupervisorService):
        self.tecnico_supervisor_service = tecnico_supervisor_service

    def validate_user_empresa_access(self, user: User, id_empresa: int) -> bool:
        """
        Validate that the user has access to the specified empresa.

        Args:
            user: User instance
            id_empresa: ID of the empresa to validate

        Returns:
            True if user has access, False otherwise
        """
        user_empresa_ids = [empresa.id for empresa in user.empresas]
        return id_empresa in user_empresa_ids

    def add_tecnicos_supervisores(
        self, user: User, tecnicos_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Add multiple tecnico supervisor records.

        Args:
            user: User creating the records
            tecnicos_data: List of dictionaries with tecnico data

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate input data
        if not isinstance(tecnicos_data, list):
            raise ValueError("Los datos de entrada deben ser una lista")

        if not tecnicos_data:
            raise ValueError("Debe proporcionar al menos un técnico")

        # Get user's empresa (assuming user has at least one empresa)
        if not user.empresas:
            raise ValueError("El usuario no tiene empresas asociadas")

        # For now, we'll use the first empresa of the user
        # You might want to modify this logic based on your requirements
        user_empresa_id = user.empresas[0].id

        # Validate each tecnico data
        validated_tecnicos = []
        errors = []

        for i, tecnico_data in enumerate(tecnicos_data):
            if not isinstance(tecnico_data, dict):
                errors.append(f"Técnico {i + 1}: Debe ser un diccionario")
                continue

            # Required fields
            required_fields = ["nombre_tecnico", "rut_tecnico", "nombre_supervisor"]
            missing_fields = [
                field
                for field in required_fields
                if not tecnico_data.get(field, "").strip()
            ]

            if missing_fields:
                errors.append(
                    f"Técnico {i + 1}: Campos requeridos faltantes: {', '.join(missing_fields)}"
                )
                continue

            # Validate field lengths
            nombre_tecnico = tecnico_data["nombre_tecnico"].strip()
            rut_tecnico = tecnico_data["rut_tecnico"].strip()
            nombre_supervisor = tecnico_data["nombre_supervisor"].strip()

            if len(nombre_tecnico) > 128:
                errors.append(
                    f"Técnico {i + 1}: El nombre del técnico no puede exceder los 128 caracteres"
                )
                continue

            if len(rut_tecnico) > 16:
                errors.append(
                    f"Técnico {i + 1}: El RUT no puede exceder los 16 caracteres"
                )
                continue

            if len(nombre_supervisor) > 128:
                errors.append(
                    f"Técnico {i + 1}: El nombre del supervisor no puede exceder los 128 caracteres"
                )
                continue

            # Add empresa ID to the validated data
            validated_tecnico = {
                "nombre_tecnico": nombre_tecnico,
                "rut_tecnico": rut_tecnico,
                "nombre_supervisor": nombre_supervisor,
                "id_empresa": user_empresa_id,
            }

            validated_tecnicos.append(validated_tecnico)

        if errors:
            raise ValueError(f"Errores de validación: {'; '.join(errors)}")

        # Create the records
        try:
            result = self.tecnico_supervisor_service.create_tecnicos_supervisores_bulk(
                validated_tecnicos
            )

            message_parts = []
            if result["created_count"] > 0:
                message_parts.append(
                    f"Se crearon {result['created_count']} técnicos exitosamente"
                )

            message = (
                ". ".join(message_parts)
                if message_parts
                else "No se procesaron técnicos"
            )

            return {
                "success": True,
                "message": message,
                "created_count": result["created_count"],
                "created_ids": result["created_ids"],
                "total_count": result["total_count"],
            }

        except Exception as e:
            raise RuntimeError(f"Error de base de datos: {str(e)}") from e

    def get_tecnicos_for_user_empresa(self, user: User) -> dict[str, Any]:
        """
        Get all tecnicos for the user's empresa.

        Args:
            user: User requesting the tecnicos

        Returns:
            Dictionary with tecnicos data

        Raises:
            ValueError: If validation fails
        """
        if not user.empresas:
            raise ValueError("El usuario no tiene empresas asociadas")

        # Use the first empresa of the user
        user_empresa_id = user.empresas[0].id

        tecnicos = self.tecnico_supervisor_service.get_tecnicos_by_empresa(
            user_empresa_id
        )

        return {
            "empresa_id": user_empresa_id,
            "empresa_nombre": user.empresas[0].nombre,
            "tecnicos": [
                {
                    "id": tecnico.id,
                    "nombre_tecnico": tecnico.nombre_tecnico,
                    "rut_tecnico": tecnico.rut_tecnico,
                    "nombre_supervisor": tecnico.nombre_supervisor,
                    "created_at": tecnico.created_at.isoformat(),
                }
                for tecnico in tecnicos
            ],
        }

    def get_all_tecnicos_supervisores(self) -> dict[str, Any]:
        """
        Get all tecnicos supervisores from all empresas.

        Returns:
            Dictionary with all tecnicos data
        """
        tecnicos = self.tecnico_supervisor_service.get_all_tecnicos_supervisores()

        return {
            "tecnicos_supervisores": [
                {
                    "id": tecnico.id,
                    "nombre_tecnico": tecnico.nombre_tecnico,
                    "rut_tecnico": tecnico.rut_tecnico,
                    "nombre_supervisor": tecnico.nombre_supervisor,
                    "id_empresa": tecnico.id_empresa,
                    "created_at": tecnico.created_at.isoformat(),
                    "updated_at": tecnico.updated_at.isoformat(),
                    "active": tecnico.active,
                }
                for tecnico in tecnicos
            ],
            "total": len(tecnicos),
        }
