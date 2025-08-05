from src.models import db
from src.models.base import BaseModel
from sqlalchemy import String
from typing import Any


class EmpresasExternasToa(BaseModel):
    __tablename__ = "empresas_externas_toa"
    nombre = db.Column(String(200), nullable=False)
    nombre_toa = db.Column(String(200), nullable=False)
    rut = db.Column(String(200), nullable=False)

    @classmethod
    def get_empresas_externas_toa_all(cls) -> list[dict[str, Any]]:
        return cls.query.all()

    @classmethod
    def set_empresas_externas_toa(cls, nombre: str, nombre_toa: str, rut: str) -> bool:
        try:
            nueva_empresa = cls(nombre=nombre, nombre_toa=nombre_toa, rut=rut)
            db.session.add(nueva_empresa)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return True
