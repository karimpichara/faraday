from typing import Any, Optional

from werkzeug.datastructures import FileStorage

from src.models.auth.user import User
from src.models.orden_trabajo import OrdenTrabajo
from src.services.comentarios_service import ComentariosService
from src.services.orden_trabajo_service import OrdenTrabajoService

# Constants
ORDER_ACCESS_DENIED_MESSAGE = (
    "Orden de trabajo '{}' no encontrada o el usuario no tiene acceso"
)


class ComentariosUseCase:
    """Use case for managing comentarios operations."""

    def __init__(
        self,
        comentarios_service: ComentariosService,
        orden_trabajo_service: OrdenTrabajoService,
    ):
        self.comentarios_service = comentarios_service
        self.orden_trabajo_service = orden_trabajo_service

    def validate_user_access_to_orden(
        self, user: User, orden_trabajo: OrdenTrabajo
    ) -> bool:
        """
        Validate that the user has access to the empresa associated with the orden de trabajo.
        Admin users (dev user or users with admin role) have access to all ordenes.

        Args:
            user: User instance
            orden_trabajo: OrdenTrabajo instance

        Returns:
            True if user has access, False otherwise
        """
        # Check if user is admin (dev user or has admin role)
        is_admin = user.username == "dev" or user.has_roles(["admin"])

        if is_admin:
            return True

        user_empresa_ids = [empresa.id for empresa in user.empresas]
        return orden_trabajo.id_empresa in user_empresa_ids

    def get_orden_trabajo_by_codigo(self, codigo: str) -> OrdenTrabajo | None:
        """
        Get orden de trabajo by codigo.

        Args:
            codigo: Orden de trabajo codigo

        Returns:
            OrdenTrabajo instance or None if not found
        """
        return self.orden_trabajo_service.get_orden_trabajo_by_codigo(codigo)

    def add_comentario(
        self,
        user: User,
        codigo_orden_trabajo: str,
        comentario_data: dict[str, Any],
        imagen: Optional[FileStorage] = None,
    ) -> dict[str, Any]:
        """
        Add a comentario to an orden de trabajo.

        Args:
            user: User making the comment
            codigo_orden_trabajo: Orden de trabajo codigo
            comentario_data: Dictionary with 'comentario' and 'num_ticket' keys
            imagen: Optional image file upload

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate input data
        if not isinstance(comentario_data, dict):
            raise ValueError("Los datos del comentario deben ser un diccionario")

        comentario_text = comentario_data.get("comentario", "").strip()
        num_ticket = comentario_data.get("num_ticket", "").strip()

        if not comentario_text or not num_ticket:
            raise ValueError(
                "Tanto 'comentario' como 'num_ticket' son requeridos y no pueden estar vacíos"
            )

        if len(comentario_text) > 256:
            raise ValueError("El comentario no puede exceder los 256 caracteres")

        if len(num_ticket) > 32:
            raise ValueError("El número de ticket no puede exceder los 32 caracteres")

        # Get orden de trabajo and validate user access (combined for security)
        orden_trabajo = self.get_orden_trabajo_by_codigo(codigo_orden_trabajo)
        if not orden_trabajo or not self.validate_user_access_to_orden(
            user, orden_trabajo
        ):
            raise ValueError(ORDER_ACCESS_DENIED_MESSAGE.format(codigo_orden_trabajo))

        # Create comentario
        try:
            comentario = self.comentarios_service.create_comentario(
                comentario=comentario_text,
                num_ticket=num_ticket,
                id_orden_trabajo=orden_trabajo.id,
                id_usuario=user.id,
                imagen=imagen,
            )

            return {
                "success": True,
                "message": "Comment added successfully",
                "comentario_id": comentario.id,
            }

        except Exception as e:
            raise RuntimeError(f"Error al crear el comentario: {str(e)}") from e

    def get_comentarios_count_for_orden(
        self,
        user: User,
        codigo_orden_trabajo: str,
    ) -> dict[str, Any]:
        """
        Get comentarios count for an orden de trabajo if user has access.

        Args:
            user: User requesting the count
            codigo_orden_trabajo: Orden de trabajo codigo

        Returns:
            Dictionary with orden data and comentarios count

        Raises:
            ValueError: If validation fails
        """
        # Get orden de trabajo and validate user access (combined for security)
        orden_trabajo = self.get_orden_trabajo_by_codigo(codigo_orden_trabajo)
        if not orden_trabajo or not self.validate_user_access_to_orden(
            user, orden_trabajo
        ):
            raise ValueError(ORDER_ACCESS_DENIED_MESSAGE.format(codigo_orden_trabajo))

        # Get comentarios count
        comentarios_count = (
            self.comentarios_service.get_comentarios_count_by_orden_trabajo(
                orden_trabajo.id
            )
        )

        return {
            "orden_trabajo": {
                "id": orden_trabajo.id,
                "codigo": orden_trabajo.codigo,
                "id_empresa": orden_trabajo.id_empresa,
            },
            "comentarios_count": comentarios_count,
        }

    def get_comentarios_for_orden(
        self,
        user: User,
        codigo_orden_trabajo: str,
    ) -> dict[str, Any]:
        """
        Get all comentarios for an orden de trabajo if user has access.

        Args:
            user: User requesting the comments
            codigo_orden_trabajo: Orden de trabajo codigo

        Returns:
            Dictionary with comentarios data

        Raises:
            ValueError: If validation fails
        """
        # Get orden de trabajo and validate user access (combined for security)
        orden_trabajo = self.get_orden_trabajo_by_codigo(codigo_orden_trabajo)
        if not orden_trabajo or not self.validate_user_access_to_orden(
            user, orden_trabajo
        ):
            raise ValueError(ORDER_ACCESS_DENIED_MESSAGE.format(codigo_orden_trabajo))

        # Get comentarios
        comentarios = self.comentarios_service.get_comentarios_by_orden_trabajo(
            orden_trabajo.id
        )

        return {
            "orden_trabajo": {
                "id": orden_trabajo.id,
                "codigo": orden_trabajo.codigo,
                "id_empresa": orden_trabajo.id_empresa,
            },
            "comentarios": [
                {
                    "id": comentario.id,
                    "comentario": comentario.comentario,
                    "num_ticket": comentario.num_ticket,
                    "created_at": comentario.created_at.isoformat(),
                    "id_usuario": comentario.id_usuario,
                    "imagen_path": comentario.imagen_path,
                    "imagen_original_name": comentario.imagen_original_name,
                }
                for comentario in comentarios
            ],
        }

    def get_all_comentarios(self) -> dict[str, Any]:
        """
        Get all comentarios from the system.

        Returns:
            Dictionary with all comentarios data

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            # Get all comentarios through service
            comentarios = self.comentarios_service.get_all_comentarios()

            return {
                "comentarios": [
                    {
                        "id": comentario.id,
                        "comentario": comentario.comentario,
                        "num_ticket": comentario.num_ticket,
                        "created_at": comentario.created_at.isoformat(),
                        "id_usuario": comentario.id_usuario,
                        "id_orden_trabajo": comentario.id_orden_trabajo,
                        "imagen_path": comentario.imagen_path,
                        "imagen_original_name": comentario.imagen_original_name,
                    }
                    for comentario in comentarios
                ],
                "total": len(comentarios),
            }

        except Exception as e:
            raise RuntimeError(f"Error al obtener comentarios: {str(e)}") from e

    def get_all_comentarios_for_admin(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        """
        Get paginated comentarios from the system including inactive ones (for admin panel).

        Args:
            page: Page number (1-based)
            per_page: Number of items per page

        Returns:
            Dictionary with paginated comentarios data including inactive ones

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            # Get paginated comentarios
            pagination_result = self.comentarios_service.get_comentarios_paginated(
                page, per_page
            )

            # Get total counts for statistics (we need all comentarios for this)
            all_comentarios = (
                self.comentarios_service.get_all_comentarios_including_inactive()
            )
            total_count = len(all_comentarios)
            active_count = len([c for c in all_comentarios if c.active])
            inactive_count = len([c for c in all_comentarios if not c.active])

            return {
                "comentarios": [
                    {
                        "id": comentario.id,
                        "comentario": comentario.comentario,
                        "num_ticket": comentario.num_ticket,
                        "created_at": comentario.created_at.isoformat(),
                        "updated_at": comentario.updated_at.isoformat(),
                        "id_usuario": comentario.id_usuario,
                        "id_orden_trabajo": comentario.id_orden_trabajo,
                        "imagen_path": comentario.imagen_path,
                        "imagen_original_name": comentario.imagen_original_name,
                        "active": comentario.active,
                    }
                    for comentario in pagination_result["items"]
                ],
                "pagination": {
                    "page": pagination_result["page"],
                    "per_page": pagination_result["per_page"],
                    "pages": pagination_result["pages"],
                    "total": pagination_result["total"],
                    "has_prev": pagination_result["has_prev"],
                    "has_next": pagination_result["has_next"],
                    "prev_num": pagination_result["prev_num"],
                    "next_num": pagination_result["next_num"],
                },
                "total": total_count,
                "active_count": active_count,
                "inactive_count": inactive_count,
            }

        except Exception as e:
            raise RuntimeError(f"Error al obtener comentarios: {str(e)}") from e

    def soft_delete_comentario(self, comentario_id: int) -> dict[str, Any]:
        """
        Soft delete a comentario (admin only operation).

        Args:
            comentario_id: Comentario ID

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If comentario not found
            RuntimeError: If database operation fails
        """
        try:
            # Get comentario to verify it exists
            comentario = self.comentarios_service.get_comentario_by_id(comentario_id)
            if not comentario:
                raise ValueError(f"Comentario con ID {comentario_id} no encontrado")

            if not comentario.active:
                raise ValueError("El comentario ya está inactivo")

            # Soft delete the comentario
            success = self.comentarios_service.soft_delete_comentario(comentario_id)
            if not success:
                raise RuntimeError("Error al desactivar el comentario")

            return {
                "success": True,
                "message": f"Comentario #{comentario_id} desactivado exitosamente",
                "comentario_id": comentario_id,
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise RuntimeError(f"Error al desactivar comentario: {str(e)}") from e

    def restore_comentario(self, comentario_id: int) -> dict[str, Any]:
        """
        Restore a soft deleted comentario (admin only operation).

        Args:
            comentario_id: Comentario ID

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If comentario not found
            RuntimeError: If database operation fails
        """
        try:
            # Get comentario to verify it exists
            comentario = self.comentarios_service.get_comentario_by_id(comentario_id)
            if not comentario:
                raise ValueError(f"Comentario con ID {comentario_id} no encontrado")

            if comentario.active:
                raise ValueError("El comentario ya está activo")

            # Restore the comentario
            success = self.comentarios_service.restore_comentario(comentario_id)
            if not success:
                raise RuntimeError("Error al restaurar el comentario")

            return {
                "success": True,
                "message": f"Comentario #{comentario_id} restaurado exitosamente",
                "comentario_id": comentario_id,
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise RuntimeError(f"Error al restaurar comentario: {str(e)}") from e
