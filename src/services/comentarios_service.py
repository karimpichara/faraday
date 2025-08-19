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
        Get all ACTIVE comentarios for a specific orden de trabajo.

        Args:
            id_orden_trabajo: Orden de trabajo ID

        Returns:
            List of active Comentario instances ordered by creation date (newest first)
        """
        return (
            Comentario.active_records()
            .filter_by(id_orden_trabajo=id_orden_trabajo)
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
        Get the count of ACTIVE comentarios for a specific orden de trabajo.

        Args:
            id_orden_trabajo: Orden de trabajo ID

        Returns:
            Number of active comentarios for the orden de trabajo
        """
        return (
            Comentario.active_records()
            .filter_by(id_orden_trabajo=id_orden_trabajo)
            .count()
        )

    def get_all_comentarios(self) -> list[Comentario]:
        """
        Get all ACTIVE comentarios from the system.

        Returns:
            List of all active Comentario instances ordered by creation date (newest first)
        """
        return Comentario.active_records().order_by(Comentario.created_at.desc()).all()

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

    def soft_delete_comentario(self, comentario_id: int) -> bool:
        """
        Soft delete a comentario (mark as inactive).

        Args:
            comentario_id: Comentario ID

        Returns:
            True if soft deleted successfully, False otherwise
        """
        try:
            comentario = Comentario.query.get(comentario_id)
            if not comentario:
                return False

            comentario.soft_delete()
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            return False

    def get_all_comentarios_including_inactive(self) -> list[Comentario]:
        """
        Get all comentarios from the system including inactive ones.

        Returns:
            List of all Comentario instances (active and inactive) ordered by creation date
        """
        return Comentario.query.order_by(Comentario.created_at.desc()).all()

    def get_comentarios_paginated(self, page: int = 1, per_page: int = 20) -> dict:
        """
        Get paginated comentarios including inactive ones.

        Args:
            page: Page number (1-based)
            per_page: Number of items per page

        Returns:
            Dictionary with paginated results
        """
        paginated = Comentario.query.order_by(Comentario.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return {
            "items": paginated.items,
            "total": paginated.total,
            "page": paginated.page,
            "per_page": paginated.per_page,
            "pages": paginated.pages,
            "has_prev": paginated.has_prev,
            "has_next": paginated.has_next,
            "prev_num": paginated.prev_num,
            "next_num": paginated.next_num,
        }

    def restore_comentario(self, comentario_id: int) -> bool:
        """
        Restore a soft deleted comentario.

        Args:
            comentario_id: Comentario ID

        Returns:
            True if restored successfully, False otherwise
        """
        try:
            comentario = Comentario.query.get(comentario_id)
            if not comentario:
                return False

            comentario.restore()
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            return False
