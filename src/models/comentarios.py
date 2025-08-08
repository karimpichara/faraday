from sqlalchemy import String

from src.models import db
from src.models._base import BaseModel


class Comentario(BaseModel):
    __tablename__ = "comentarios"
    comentario = db.Column(String(256), nullable=False)
    num_ticket = db.Column(String(32), nullable=False)
    imagen_path = db.Column(String(512), nullable=True)  # Optional image file path
    imagen_original_name = db.Column(String(256), nullable=True)  # Original filename
    id_orden_trabajo = db.Column(
        db.Integer, db.ForeignKey("ordenes_trabajo.id"), nullable=False
    )
    id_usuario = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    orden_trabajo = db.relationship("OrdenTrabajo", backref="comentarios")
