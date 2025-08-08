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
