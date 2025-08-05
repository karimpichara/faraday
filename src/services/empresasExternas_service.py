from typing import Any
from src.models.empresas_externas_toa import EmpresasExternasToa


class EmpresasExternasService:
    def get_empresas_externas_toa_all(self) -> list[dict[str, Any]]:
        return EmpresasExternasToa.get_empresas_externas_toa_all()

    def set_empresas_externas_toa(self, nombre: str, nombre_toa: str, rut: str) -> bool:
        return EmpresasExternasToa.set_empresas_externas_toa(nombre, nombre_toa, rut)
