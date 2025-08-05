from src.services.historia_iniciados_service import HistoriaIniciadosService
from src.services.empresasExternas_service import EmpresasExternasService
from typing import Any


class HistoriaIniciadosUseCase:
    def __init__(
        self,
        historia_iniciados_service: HistoriaIniciadosService,
        empresas_externas_service: EmpresasExternasService,
    ):
        self.historia_iniciados_service = historia_iniciados_service
        self.empresas_externas_service = empresas_externas_service

    def set_data_zona_sur(self, data: list[dict[str, Any]]) -> None:
        empresas_externas = (
            self.empresas_externas_service.get_empresas_externas_toa_all()
        )
        ot_no_ingresadas = []
        for item in data:
            validador = False
            for empresa in empresas_externas:
                empresa_toa = empresa["nombre_toa"]
                if empresa_toa in item["Técnico"]:
                    self.historia_iniciados_service.set_data_to_database(
                        item, "sur", empresa["nombre_toa"]
                    )
                    validador = True
                    break
            if not validador:
                ot_no_ingresadas.append(item)
        return ot_no_ingresadas

    def set_data_zona_norte(self, data: list[dict[str, Any]]) -> None:
        empresas_externas = (
            self.empresas_externas_service.get_empresas_externas_toa_all()
        )
        ot_no_ingresadas = []
        for item in data:
            validador = False
            for empresa in empresas_externas:
                empresa_toa = empresa["nombre_toa"]
                if empresa_toa in item["Técnico"]:
                    self.historia_iniciados_service.set_data_to_database(
                        item, "norte", empresa["nombre_toa"]
                    )
                    validador = True
                    break
            if not validador:
                ot_no_ingresadas.append(item)
        return ot_no_ingresadas

    def set_data_zona_centro(self, data: list[dict[str, Any]]) -> None:
        empresas_externas = (
            self.empresas_externas_service.get_empresas_externas_toa_all()
        )
        ot_no_ingresadas = []
        for item in data:
            validador = False
            for empresa in empresas_externas:
                empresa_toa = empresa["nombre_toa"]
                if empresa_toa in item["Técnico"]:
                    self.historia_iniciados_service.set_data_to_database(
                        item, "centro", empresa["nombre_toa"]
                    )
                    validador = True
                    break
            if not validador:
                ot_no_ingresadas.append(item)
        return ot_no_ingresadas

    def set_data_zona_metropolitana(self, data: list[dict[str, Any]]) -> None:
        empresas_externas = (
            self.empresas_externas_service.get_empresas_externas_toa_all()
        )
        ot_no_ingresadas = []
        for item in data:
            validador = False
            for empresa in empresas_externas:
                empresa_toa = empresa["nombre_toa"]
                if empresa_toa in item["Técnico"]:
                    self.historia_iniciados_service.set_data_to_database(
                        item, "metropolitana", empresa["nombre_toa"]
                    )
                    validador = True
                    break
            if not validador:
                ot_no_ingresadas.append(item)
        return ot_no_ingresadas

    def set_empresas_externas_toa(self, data: dict[str, Any]) -> bool:
        result = self.empresas_externas_service.set_empresas_externas_toa(
            data["nombre"], data["nombre_toa"], data["rut"]
        )
        if not result:
            raise Exception("Error al setear la empresa externa en la base de datos")
        return True
