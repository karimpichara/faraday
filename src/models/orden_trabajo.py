from sqlalchemy import String

from src.models import db
from src.models._base import BaseModel


class OrdenTrabajo(BaseModel):
    __tablename__ = "ordenes_trabajo"
    codigo = db.Column(String(32), nullable=False)
    id_empresa = db.Column(
        db.Integer, db.ForeignKey("empresas_externas_toa.id"), nullable=False
    )

    empresas_externas_toa = db.relationship(
        "EmpresasExternasToa", backref="ordenes_trabajo"
    )
