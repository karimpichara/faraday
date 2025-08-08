from src.models import db
from src.models.comentarios import Comentario


class ComentariosService:
    """Service for managing comentarios operations."""

    def create_comentario(
        self,
        comentario: str,
        num_ticket: str,
        id_orden_trabajo: int,
        id_usuario: int,
    ) -> Comentario:
        """
        Create a new comentario.

        Args:
            comentario: Comment text
            num_ticket: Ticket number
            id_orden_trabajo: Orden de trabajo ID
            id_usuario: User ID

        Returns:
            Created Comentario instance

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            nuevo_comentario = Comentario(
                comentario=comentario.strip(),
                num_ticket=num_ticket.strip(),
                id_orden_trabajo=id_orden_trabajo,
                id_usuario=id_usuario,
            )

            db.session.add(nuevo_comentario)
            db.session.commit()
            return nuevo_comentario

        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al crear el comentario: {str(e)}") from e

    def get_comentarios_by_orden_trabajo(
        self, id_orden_trabajo: int
    ) -> list[Comentario]:
        """
        Get all comentarios for a specific orden de trabajo.

        Args:
            id_orden_trabajo: Orden de trabajo ID

        Returns:
            List of Comentario instances ordered by creation date (newest first)
        """
        return (
            Comentario.query.filter_by(id_orden_trabajo=id_orden_trabajo)
            .order_by(Comentario.created_at.desc())
            .all()
        )

    def get_comentario_by_id(self, comentario_id: int) -> Comentario | None:
        """
        Get a comentario by its ID.

        Args:
            comentario_id: Comentario ID

        Returns:
            Comentario instance or None if not found
        """
        return Comentario.query.get(comentario_id)

    def get_comentarios_count_by_orden_trabajo(self, id_orden_trabajo: int) -> int:
        """
        Get the count of comentarios for a specific orden de trabajo.

        Args:
            id_orden_trabajo: Orden de trabajo ID

        Returns:
            Number of comentarios for the orden de trabajo
        """
        return Comentario.query.filter_by(id_orden_trabajo=id_orden_trabajo).count()
