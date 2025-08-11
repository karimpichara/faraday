from typing import Any

from src.services.user_service import UserService

# Constants
INVALID_USER_ID_MESSAGE = "ID de usuario inválido"


class UserUseCase:
    """Use case for managing user operations."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def create_user(
        self,
        username: str,
        password: str,
        empresa_id: int,
    ) -> dict[str, Any]:
        """
        Create a new user with supervisor role and assigned empresa.

        Args:
            username: Username for the new user
            password: Password for the new user
            empresa_id: ID of the empresa to assign to the user

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate input data
        if not username or not password:
            raise ValueError("Usuario y contraseña son requeridos")

        if len(username.strip()) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres")

        if len(password.strip()) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres")

        if not isinstance(empresa_id, int) or empresa_id <= 0:
            raise ValueError("ID de empresa inválido")

        # Create user through service
        user = self.user_service.create_user(
            username=username.strip(),
            password=password.strip(),
            empresa_id=empresa_id,
        )

        return {
            "success": True,
            "message": f"Usuario '{user.username}' creado exitosamente",
            "user_id": user.id,
        }

    def get_all_users_data(self) -> dict[str, Any]:
        """
        Get all users with their associated data.

        Returns:
            Dictionary with users data including empresas info
        """
        users = self.user_service.get_all_users()

        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "roles": [role.name for role in user.roles],
                    "empresas": [
                        {
                            "id": empresa.id,
                            "nombre": empresa.nombre,
                            "nombre_toa": empresa.nombre_toa,
                        }
                        for empresa in user.empresas
                    ],
                    "created_at": user.created_at.isoformat(),
                    "is_dev": user.username == "dev",
                }
                for user in users
            ],
            "total": len(users),
        }

    def get_inactive_users_data(self) -> dict[str, Any]:
        """
        Get all inactive (soft-deleted) users with their associated data.

        Returns:
            Dictionary with inactive users data
        """
        from src.models.auth.user import User

        # Get only inactive users
        inactive_users = User.query.filter_by(active=False).all()

        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "roles": [role.name for role in user.roles],
                    "empresas": [
                        {
                            "id": empresa.id,
                            "nombre": empresa.nombre,
                            "nombre_toa": empresa.nombre_toa,
                        }
                        for empresa in user.empresas
                    ],
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                    "is_dev": user.username == "dev",
                    "is_inactive": True,
                }
                for user in inactive_users
            ],
            "total": len(inactive_users),
        }

    def get_empresas_for_dropdown(self) -> dict[str, Any]:
        """
        Get all empresas for dropdown selection.

        Returns:
            Dictionary with empresas data for form dropdowns
        """
        empresas = self.user_service.get_all_empresas()

        return {
            "empresas": [
                {
                    "id": empresa.id,
                    "nombre": empresa.nombre,
                    "nombre_toa": empresa.nombre_toa,
                    "display_name": f"{empresa.nombre} ({empresa.nombre_toa})",
                }
                for empresa in empresas
            ]
        }

    def update_user(
        self,
        user_id: int,
        username: str = None,
        password: str = None,
        empresa_id: int = None,
    ) -> dict[str, Any]:
        """
        Update an existing user.

        Args:
            user_id: ID of the user to update
            username: New username (optional)
            password: New password (optional)
            empresa_id: New empresa ID (optional)

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate input data
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(INVALID_USER_ID_MESSAGE)

        if username is not None:
            if len(username.strip()) < 3:
                raise ValueError("El usuario debe tener al menos 3 caracteres")
            username = username.strip()

        if password is not None:
            if len(password.strip()) < 4:
                raise ValueError("La contraseña debe tener al menos 4 caracteres")
            password = password.strip()

        if empresa_id is not None and (
            not isinstance(empresa_id, int) or empresa_id <= 0
        ):
            raise ValueError("ID de empresa inválido")

        # Update user through service
        user = self.user_service.update_user(
            user_id=user_id,
            username=username,
            password=password,
            empresa_id=empresa_id,
        )

        return {
            "success": True,
            "message": f"Usuario '{user.username}' actualizado exitosamente",
            "user_id": user.id,
        }

    def delete_user(self, user_id: int) -> dict[str, Any]:
        """
        Delete a user.

        Args:
            user_id: ID of the user to delete

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails or trying to delete dev user
            RuntimeError: If database operation fails
        """
        # Validate input data
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(INVALID_USER_ID_MESSAGE)

        # Delete user through service
        deleted = self.user_service.delete_user(user_id)

        if not deleted:
            raise ValueError("Usuario no encontrado")

        return {
            "success": True,
            "message": "Usuario eliminado exitosamente",
        }

    def restore_user(self, user_id: int) -> dict[str, Any]:
        """
        Restore a soft-deleted user.

        Args:
            user_id: ID of the user to restore

        Returns:
            Dictionary with operation results

        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        # Validate input data
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(INVALID_USER_ID_MESSAGE)

        # Restore user through service
        restored = self.user_service.restore_user(user_id)

        if not restored:
            raise ValueError("Usuario no encontrado o ya está activo")

        return {
            "success": True,
            "message": "Usuario restaurado exitosamente",
        }

    def get_user_details(self, user_id: int) -> dict[str, Any]:
        """
        Get detailed information about a specific user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with user details

        Raises:
            ValueError: If user not found
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "roles": [role.name for role in user.roles],
                "empresas": [
                    {
                        "id": empresa.id,
                        "nombre": empresa.nombre,
                        "nombre_toa": empresa.nombre_toa,
                    }
                    for empresa in user.empresas
                ],
                "created_at": user.created_at.isoformat(),
                "is_dev": user.username == "dev",
            }
        }
