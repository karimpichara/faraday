import json
from typing import Any

from src.services.empresas_externas_service import EmpresasExternasService
from src.services.historia_iniciados_service import HistoriaIniciadosService


class HistoriaIniciadosUseCase:
    def __init__(
        self,
        historia_iniciados_service: HistoriaIniciadosService,
        empresas_externas_service: EmpresasExternasService,
    ):
        self.historia_iniciados_service = historia_iniciados_service
        self.empresas_externas_service = empresas_externas_service

    def set_data_zona(
        self, data: list[dict[str, Any]], zona: str
    ) -> list[dict[str, Any]]:
        """
        Efficiently processes data for any zona by matching técnico names with empresas externas.

        Args:
            data: List of items to process, each containing a "Técnico" field
            zona: Zone name (sur, norte, centro, metropolitana, etc.)

        Returns:
            List of items that couldn't be matched with any empresa externa
        """
        # Get empresas externas once and cache the lookup
        empresas_externas = (
            self.empresas_externas_service.get_empresas_externas_toa_all()
        )
        empresa_nombres = [empresa.nombre_toa for empresa in empresas_externas]

        ot_no_ingresadas = []

        for item in data:
            tecnico = item.get("Técnico", "")
            empresa_encontrada = None

            # Find the first matching empresa in the técnico field
            for empresa_nombre in empresa_nombres:
                if empresa_nombre in tecnico:
                    empresa_encontrada = empresa_nombre
                    break

            if empresa_encontrada:
                self.historia_iniciados_service.set_data_to_database(
                    item, zona, empresa_encontrada
                )
            else:
                ot_no_ingresadas.append(item)

        return ot_no_ingresadas

    def set_data_zona_sur(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process data for zona sur"""
        return self.set_data_zona(data, "sur")

    def set_data_zona_norte(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process data for zona norte"""
        return self.set_data_zona(data, "norte")

    def set_data_zona_centro(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Process data for zona centro"""
        return self.set_data_zona(data, "centro")

    def set_data_zona_metropolitana(
        self, data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Process data for zona metropolitana"""
        return self.set_data_zona(data, "metropolitana")

    def set_empresas_externas_toa(self, data: dict[str, Any]) -> bool:
        result = self.empresas_externas_service.set_empresas_externas_toa(
            data["nombre"], data["nombre_toa"], data["rut"]
        )
        if not result:
            raise ValueError("Error al setear la empresa externa en la base de datos")
        return True
