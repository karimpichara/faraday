from typing import Any

from src.models.historia_ot_empresas import HistoriaOtEmpresas


class HistoriaIniciadosService:
    def set_data_to_database(
        self, data: dict[str, Any], zona: str, empresa: str
    ) -> None:
        for item in data:
            HistoriaOtEmpresas.set_historia_iniciados(item, zona, empresa)

    def get_historia_iniciados(self) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_all()

    def get_historia_iniciados_by_zona(self, zona: str) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_by_zona(zona)

    def get_historia_iniciados_by_zona_and_fecha(
        self, zona: str, fecha: str
    ) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_by_zona_and_fecha(zona, fecha)

    def get_historia_iniciados_by_ot(self, ot: str) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_by_ot(ot)

    def get_historia_iniciados_by_ot_and_fecha(
        self, ot: str, fecha: str
    ) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_by_ot_and_fecha(ot, fecha)

    def get_historia_iniciados_by_empresa(self, empresa: str) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_by_empresa(empresa)

    def get_historia_iniciados_by_rango_fecha(
        self, fecha_inicio: str, fecha_fin: str
    ) -> list[dict[str, Any]]:
        return HistoriaOtEmpresas.get_historia_iniciados_by_rango_fecha(
            fecha_inicio, fecha_fin
        )
