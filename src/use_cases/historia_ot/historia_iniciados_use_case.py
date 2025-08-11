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
        try:
            data = json.load(data)
        except Exception as e:
            raise Exception(f"Error al cargar el archivo: {e}")
        for item in data:
            tecnico = item.get("Técnico", "")
            empresa_encontrada = None
            # Find the first matching empresa in the técnico field
            # Handle None values gracefully
            if tecnico is None:
                tecnico = ""

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
        ot_ingresadas = len(data) - len(ot_no_ingresadas)
        cantidad_ot_rechazadas = len(ot_no_ingresadas)
        print(f"ot ingresadas: {ot_ingresadas}")
        print(f"ot rechazadas: {cantidad_ot_rechazadas}")
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

    def get_all_historia_ot_empresas(self) -> dict[str, Any]:
        """
        Get all historia OT empresas from the system.

        Returns:
            Dictionary with all historia OT empresas data

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            # Get all historia records through service
            historia_records = self.historia_iniciados_service.get_historia_iniciados()

            return {
                "historia_ot_empresas": [
                    {
                        "id": record.id,
                        "zona": record.zona,
                        "orden_de_trabajo": record.orden_de_trabajo,
                        "empresa": record.empresa,
                        "tecnico": record.tecnico,
                        "coord_x": record.coord_x,
                        "coord_y": record.coord_y,
                        "duracion": record.duracion,
                        "estado": record.estado,
                        "fecha": record.fecha,
                        "flag_consulta_vecino": record.flag_consulta_vecino,
                        "flag_estado_aprovision": record.flag_estado_aprovision,
                        "flag_fallas_masivas": record.flag_fallas_masivas,
                        "flag_materiales": record.flag_materiales,
                        "flag_niveles": record.flag_niveles,
                        "hora_flag_estado_aprovision": record.hora_flag_estado_aprovision,
                        "hora_flag_fallas_masivas": record.hora_flag_fallas_masivas,
                        "hora_flag_materiales": record.hora_flag_materiales,
                        "hora_flag_niveles": record.hora_flag_niveles,
                        "inicio": record.inicio,
                        "intervencion_neutra": record.intervencion_neutra,
                        "notas_consulta_vecino": record.notas_consulta_vecino,
                        "notas_consulta_vecino_ultimo": record.notas_consulta_vecino_ultimo,
                        "qr_drop": record.qr_drop,
                        "rut_tecnico": record.rut_tecnico,
                        "tipo_red_producto": record.tipo_red_producto,
                        "hora_ultima_vecino": record.hora_ultima_vecino,
                        "hora_qr": record.hora_qr,
                        "tipo_actividad": record.tipo_actividad,
                        "zona_de_trabajo": record.zona_de_trabajo,
                        "pasos": record.pasos,
                        "pelo": record.pelo,
                        "created_at": record.created_at.isoformat(),
                        "updated_at": record.updated_at.isoformat(),
                        "active": record.active,
                    }
                    for record in historia_records
                ],
                "total": len(historia_records),
            }

        except Exception as e:
            raise RuntimeError(
                f"Error al obtener historia OT empresas: {str(e)}"
            ) from e
