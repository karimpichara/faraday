from typing import Any

from sqlalchemy import String

from src.models import db
from src.models.base import BaseModel


class HistoriaOtEmpresas(BaseModel):
    __tablename__ = "historia_ot_empresas"
    zona = db.Column(String(64), nullable=False)
    orden_de_trabajo = db.Column(String(64), nullable=False)
    empresa = db.Column(String(128), nullable=False)
    tecnico = db.Column(String(128), nullable=False)
    coord_x = db.Column(String(32), nullable=False)
    coord_y = db.Column(String(32), nullable=False)
    duracion = db.Column(String(128), nullable=False)
    estado = db.Column(String(128), nullable=False)
    fecha = db.Column(String(128), nullable=False)
    flag_consulta_vecino = db.Column(String(128), nullable=False)
    flag_estado_aprovision = db.Column(String(128), nullable=False)
    flag_fallas_masivas = db.Column(String(128), nullable=False)
    flag_materiales = db.Column(String(128), nullable=False)
    flag_niveles = db.Column(String(128), nullable=False)
    hora_flag_estado_aprovision = db.Column(String(128), nullable=False)
    hora_flag_fallas_masivas = db.Column(String(128), nullable=False)
    hora_flag_materiales = db.Column(String(128), nullable=False)
    hora_flag_niveles = db.Column(String(128), nullable=False)
    inicio = db.Column(String(128), nullable=False)
    intervencion_neutra = db.Column(String(128), nullable=False)
    notas_consulta_vecino = db.Column(String(8000), nullable=True)
    notas_consulta_vecino_ultimo = db.Column(String(8000), nullable=True)
    qr_drop = db.Column(String(128), nullable=False)
    rut_tecnico = db.Column(String(128), nullable=False)
    tipo_red_producto = db.Column(String(128), nullable=False)
    hora_ultima_vecino = db.Column(String(128), nullable=True)
    hora_qr = db.Column(String(128), nullable=False)
    tipo_actividad = db.Column(String(128), nullable=False)
    zona_de_trabajo = db.Column(String(128), nullable=False)

    @classmethod
    def get_historia_iniciados_all(cls) -> list[dict[str, Any]]:
        return cls.query.all()

    @classmethod
    def get_historia_iniciados_by_zona(cls, zona: str) -> list[dict[str, Any]]:
        return cls.query.filter_by(zona=zona).all()

    @classmethod
    def get_historia_iniciados_by_zona_and_fecha(
        cls, zona: str, fecha: str
    ) -> list[dict[str, Any]]:
        return cls.query.filter_by(zona=zona, fecha=fecha).all()

    @classmethod
    def get_historia_iniciados_by_ot(cls, ot: str) -> list[dict[str, Any]]:
        return cls.query.filter_by(orden_de_trabajo=ot).all()

    @classmethod
    def get_historia_iniciados_by_ot_and_fecha(
        cls, ot: str, fecha: str
    ) -> list[dict[str, Any]]:
        return cls.query.filter_by(orden_de_trabajo=ot, fecha=fecha).all()

    @classmethod
    def get_historia_iniciados_by_empresa(cls, empresa: str) -> list[dict[str, Any]]:
        return cls.query.filter_by(empresa=empresa).all()

    @classmethod
    def get_historia_iniciados_by_rango_fecha(
        cls, fecha_inicio: str, fecha_fin: str
    ) -> list[dict[str, Any]]:
        return cls.query.filter(cls.fecha >= fecha_inicio, cls.fecha <= fecha_fin).all()

    @classmethod
    def get_historia_iniciados_by_rango_fecha_and_zona(
        cls, fecha_inicio: str, fecha_fin: str, zona: str
    ) -> list[dict[str, Any]]:
        return cls.query.filter(
            cls.fecha >= fecha_inicio, cls.fecha <= fecha_fin, cls.zona == zona
        ).all()

    @classmethod
    def get_historia_iniciados_by_rango_fecha_and_empresa(
        cls, fecha_inicio: str, fecha_fin: str, empresa: str
    ) -> list[dict[str, Any]]:
        return cls.query.filter(
            cls.fecha >= fecha_inicio, cls.fecha <= fecha_fin, cls.empresa == empresa
        ).all()

    @classmethod
    def set_historia_iniciados(
        cls, data: dict[str, Any], zona: str, empresa: str
    ) -> (
        None
    ):  # la zona puede sur norte, centro o metropolitana, las empresas son las que aparecen en el toa
        try:
            nuevo_usuario = cls(
                zona=zona,
                empresa=empresa,
                orden_de_trabajo=data["Orden_de_Trabajo"],
                tecnico=data["Técnico"],
                coord_x=data["Coord_X"],
                coord_y=data["Coord_Y"],
                duracion=data["Duración"],
                estado=data["Estado"],
                fecha=data["Fecha"],
                flag_consulta_vecino=data["Flag Consulta Vecino"],
                flag_estado_aprovision=data["Flag Estado Aprovisión"],
                flag_fallas_masivas=data["Flag Fallas Masivas"],
                flag_materiales=data["Flag Materiales"],
                flag_niveles=data["Flag Niveles"],
                hora_flag_estado_aprovision=data["Hora Flag Estado Aprovisión"],
                hora_flag_fallas_masivas=data["Hora Flag Fallas Masivas"],
                hora_flag_materiales=data["Hora Flag Materiales"],
                hora_flag_niveles=data["Hora Flag Niveles"],
                inicio=data["Inicio"],
                intervencion_neutra=data["Intervención neutra"],
                notas_consulta_vecino=data["Notas Consulta Vecino"],
                notas_consulta_vecino_ultimo=data["Notas Consulta Vecino ultimo"],
                qr_drop=data["QR DROP"],
                rut_tecnico=data["Rut_tecnico"],
                tipo_red_producto=data["Tipo red producto"],
                hora_ultima_vecino=data["hora ultima vecino"],
                hora_qr=data["hora_QR"],
                tipo_actividad=data["tipo_actividad"],
                zona_de_trabajo=data["Zona de trabajo"],
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"error al cargar a la bd: {e}")
            raise e
