from typing import Optional

from werkzeug.datastructures import FileStorage

from src.models import db
from src.models.comentarios import Comentario
from src.utils.image_processor import ImageProcessor


class ComentariosService:
    """Service for managing comentarios operations."""

    def __init__(self):
        """Initialize the service with image processor."""
        self.image_processor = ImageProcessor()

    def create_comentario(
        self,
        comentario: str,
        num_ticket: str,
        id_orden_trabajo: int,
        id_usuario: int,
        imagen: Optional[FileStorage] = None,
    ) -> Comentario:
        """
        Create a new comentario.

        Args:
            comentario: Comment text
            num_ticket: Ticket number
            id_orden_trabajo: Orden de trabajo ID
            id_usuario: User ID
            imagen: Optional image file upload

        Returns:
            Created Comentario instance

        Raises:
            RuntimeError: If database operation fails
            ValueError: If image processing fails
        """
        imagen_path = None
        imagen_original_name = None

        try:
            # Process image if provided
            if imagen and imagen.filename:
                success, file_path, error_message = self.image_processor.save_image(
                    imagen
                )
                if not success:
                    raise ValueError(f"Error al procesar imagen: {error_message}")
                imagen_path = file_path
                imagen_original_name = imagen.filename

            # Create comentario with image info
            nuevo_comentario = Comentario(
                comentario=comentario.strip(),
                num_ticket=num_ticket.strip(),
                imagen_path=imagen_path,
                imagen_original_name=imagen_original_name,
                id_orden_trabajo=id_orden_trabajo,
                id_usuario=id_usuario,
            )

            db.session.add(nuevo_comentario)
            db.session.commit()
            return nuevo_comentario

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            db.session.rollback()
            # Clean up uploaded image if database operation fails
            if imagen_path:
                self.image_processor.delete_image(imagen_path)
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

    def delete_comentario(self, comentario_id: int) -> bool:
        """
        Delete a comentario and its associated image.

        Args:
            comentario_id: Comentario ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            comentario = Comentario.query.get(comentario_id)
            if not comentario:
                return False

            # Delete associated image if exists
            if comentario.imagen_path:
                self.image_processor.delete_image(comentario.imagen_path)

            db.session.delete(comentario)
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            return False
