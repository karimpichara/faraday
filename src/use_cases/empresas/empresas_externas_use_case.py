import json
from typing import Any

from werkzeug.datastructures import FileStorage

from src.services.empresas_externas_service import EmpresasExternasService


class EmpresasExternasUseCase:
    def __init__(self, empresas_externas_service: EmpresasExternasService):
        self.empresas_externas_service = empresas_externas_service

    def get_empresas_externas_toa_all(self) -> list[dict[str, Any]]:
        """
        Get all EmpresasExternasToa records formatted for API response.

        Returns:
            List of dictionaries with nombre, nombre_toa, and rut fields
        """
        try:
            empresas = self.empresas_externas_service.get_empresas_externas_toa_all()

            # Convert to the requested format
            result = []
            for empresa in empresas:
                result.append(
                    {
                        "id": empresa.id,
                        "nombre": empresa.nombre,
                        "nombre_toa": empresa.nombre_toa,
                        "rut": empresa.rut,
                    }
                )

            return result
        except Exception as e:
            raise RuntimeError(f"Error al obtener las empresas externas: {e}")

    def set_empresas_externas_toa(self, file: FileStorage) -> bool:
        try:
            data = json.load(file)
            for item in data:
                self.empresas_externas_service.set_empresas_externas_toa(
                    item["nombre"], item["nombre_toa"], item["rut"]
                )
        except Exception as e:
            raise RuntimeError(
                f"Error al setear las empresas externas en la base de datos: {e}"
            )
        return True

    def create_empresa(self, nombre: str, nombre_toa: str, rut: str) -> dict[str, Any]:
        """
        Create a new empresa with validation.

        Args:
            nombre: Company name
            nombre_toa: TOA system name
            rut: Tax ID

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        try:
            # Input validation
            if not nombre or not nombre.strip():
                raise ValueError("El nombre de la empresa es requerido")
            if not nombre_toa or not nombre_toa.strip():
                raise ValueError("El nombre TOA es requerido")
            if not rut or not rut.strip():
                raise ValueError("El RUT es requerido")

            # Clean inputs
            nombre = nombre.strip()
            nombre_toa = nombre_toa.strip()
            rut = rut.strip()

            # Length validation
            if len(nombre) < 2:
                raise ValueError("El nombre debe tener al menos 2 caracteres")
            if len(nombre_toa) < 2:
                raise ValueError("El nombre TOA debe tener al menos 2 caracteres")
            if len(rut) < 7:
                raise ValueError("El RUT debe tener al menos 7 caracteres")

            # Maximum length validation
            if len(nombre) > 100:
                raise ValueError("El nombre no puede exceder los 100 caracteres")
            if len(nombre_toa) > 50:
                raise ValueError("El nombre TOA no puede exceder los 50 caracteres")
            if len(rut) > 20:
                raise ValueError("El RUT no puede exceder los 20 caracteres")

            # Create empresa through service
            success = self.empresas_externas_service.set_empresas_externas_toa(
                nombre, nombre_toa, rut
            )

            if not success:
                raise RuntimeError("Error al crear la empresa en la base de datos")

            return {
                "success": True,
                "message": f"Empresa '{nombre}' creada exitosamente",
                "empresa": {"nombre": nombre, "nombre_toa": nombre_toa, "rut": rut},
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise RuntimeError(f"Error inesperado al crear la empresa: {str(e)}") from e
