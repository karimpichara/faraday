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

        Args:
            user: User instance
            orden_trabajo: OrdenTrabajo instance

        Returns:
            True if user has access, False otherwise
        """
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
                }
                for comentario in comentarios
            ],
        }
