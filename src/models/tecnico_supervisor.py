from sqlalchemy import String

from src.models import db
from src.models._base import BaseModel


class TecnicoSupervisor(BaseModel):
    __tablename__ = "tecnicos_supervisores"

    nombre_tecnico = db.Column(String(128), nullable=False)
    rut_tecnico = db.Column(String(16), nullable=False)
    nombre_supervisor = db.Column(String(128), nullable=False)
    id_empresa = db.Column(
        db.Integer, db.ForeignKey("empresas_externas_toa.id"), nullable=False
    )

    # Relationship to empresa
    empresa = db.relationship("EmpresasExternasToa", backref="tecnicos_supervisores")

    def __repr__(self):
        return f"<TecnicoSupervisor {self.nombre_tecnico} - {self.nombre_supervisor}>"
