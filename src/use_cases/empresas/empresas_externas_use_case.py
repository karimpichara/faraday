import json
from werkzeug.datastructures import FileStorage
from src.services.empresas_externas_service import EmpresasExternasService


class EmpresasExternasUseCase:
    def __init__(self, empresas_externas_service: EmpresasExternasService):
        self.empresas_externas_service = empresas_externas_service

    def set_empresas_externas_toa(self, file: FileStorage) -> bool:
        try:
            data = json.load(file)
            for item in data:
                self.empresas_externas_service.set_empresas_externas_toa(
                    item["nombre"], item["nombre_toa"], item["rut"]
                )
        except Exception as e:
            raise Exception(
                f"Error al setear las empresas externas en la base de datos: {e}"
            )
        return True
