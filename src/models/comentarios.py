from sqlalchemy import String

from src.models import db
from src.models._base import BaseModel


class Comentario(BaseModel):
    __tablename__ = "comentarios"
    comentario = db.Column(String(256), nullable=False)
    num_ticket = db.Column(String(32), nullable=False)
    id_orden_trabajo = db.Column(
        db.Integer, db.ForeignKey("ordenes_trabajo.id"), nullable=False
    )
    id_usuario = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    orden_trabajo = db.relationship("OrdenTrabajo", backref="comentarios")
