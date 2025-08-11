from typing import Optional

from src.models import db
from src.models.auth.user import Role, User, UserEmpresa, UserRole
from src.models.empresas_externas_toa import EmpresasExternasToa


class UserService:
    """Service for managing user operations."""

    def create_user(
        self,
        username: str,
        password: str,
        empresa_id: int,
    ) -> User:
        """
        Create a new user with supervisor role and assigned empresa.

        Args:
            username: Username for the new user
            password: Password for the new user
            empresa_id: ID of the empresa to assign to the user

        Returns:
            Created User instance

        Raises:
            ValueError: If username already exists or empresa doesn't exist
            RuntimeError: If database operation fails
        """
        try:
            # Check if username already exists among active users
            existing_user = User.active_records().filter_by(username=username).first()
            if existing_user:
                raise ValueError(f"El usuario '{username}' ya existe")

            # Check if empresa exists
            empresa = EmpresasExternasToa.query.get(empresa_id)
            if not empresa:
                raise ValueError(f"La empresa con ID {empresa_id} no existe")

            # Get supervisor role
            supervisor_role = Role.query.filter_by(name="supervisor").first()
            if not supervisor_role:
                raise ValueError("El rol 'supervisor' no existe en el sistema")

            # Create new user
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.flush()  # To get the user ID

            # Assign supervisor role
            user_role = UserRole(user_id=new_user.id, role_id=supervisor_role.id)
            db.session.add(user_role)

            # Assign empresa
            user_empresa = UserEmpresa(user_id=new_user.id, empresa_id=empresa_id)
            db.session.add(user_empresa)

            db.session.commit()
            return new_user

        except ValueError:
            # Re-raise validation errors
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al crear el usuario: {str(e)}") from e

    def get_all_users(self) -> list[User]:
        """
        Get all active users from the system.

        Returns:
            List of all active User instances
        """
        return User.active_records().all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get an active user by their ID.

        Args:
            user_id: User ID

        Returns:
            Active User instance or None if not found or inactive
        """
        user = User.query.get(user_id)
        return user if user and user.active else None

    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        empresa_id: Optional[int] = None,
    ) -> User:
        """
        Update an existing user.

        Args:
            user_id: ID of the user to update
            username: New username (optional)
            password: New password (optional)
            empresa_id: New empresa ID (optional)

        Returns:
            Updated User instance

        Raises:
            ValueError: If user doesn't exist or validation fails
            RuntimeError: If database operation fails
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.active:
                raise ValueError(f"Usuario con ID {user_id} no encontrado")

            # Update username if provided
            if username is not None:
                # Check if new username already exists among active users (excluding current user)
                existing_user = (
                    User.active_records()
                    .filter(User.username == username, User.id != user_id)
                    .first()
                )
                if existing_user:
                    raise ValueError(f"El usuario '{username}' ya existe")
                user.username = username

            # Update password if provided
            if password is not None:
                from werkzeug.security import generate_password_hash

                user.password = generate_password_hash(password)

            # Update empresa if provided
            if empresa_id is not None:
                # Check if empresa exists
                empresa = EmpresasExternasToa.query.get(empresa_id)
                if not empresa:
                    raise ValueError(f"La empresa con ID {empresa_id} no existe")

                # Remove existing empresa assignments
                UserEmpresa.query.filter_by(user_id=user_id).delete()

                # Add new empresa assignment
                user_empresa = UserEmpresa(user_id=user_id, empresa_id=empresa_id)
                db.session.add(user_empresa)

            db.session.commit()
            return user

        except ValueError:
            # Re-raise validation errors
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error al actualizar el usuario: {str(e)}") from e

    def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user (mark as inactive).

        Args:
            user_id: ID of the user to delete

        Returns:
            True if deleted successfully, False if user doesn't exist or already inactive

        Raises:
            ValueError: If trying to delete the 'dev' user
            RuntimeError: If database operation fails
        """
        try:
            user = User.query.get(user_id)
            if not user or not user.active:
                return False

            # Prevent deletion of 'dev' user
            if user.username == "dev":
                raise ValueError("No se puede eliminar el usuario 'dev'")

            # Soft delete user (mark as inactive)
            user.soft_delete()
            db.session.commit()
            return True

        except ValueError:
            # Re-raise validation errors
            db.session.rollback()
            raise
        except Exception:
            db.session.rollback()
            raise RuntimeError("Error al eliminar el usuario")

    def restore_user(self, user_id: int) -> bool:
        """
        Restore a soft-deleted user (mark as active).

        Args:
            user_id: ID of the user to restore

        Returns:
            True if restored successfully, False if user doesn't exist or already active

        Raises:
            RuntimeError: If database operation fails
        """
        try:
            user = User.query.get(user_id)
            if not user or user.active:
                return False

            # Restore user (mark as active)
            user.restore()
            db.session.commit()
            return True

        except Exception:
            db.session.rollback()
            raise RuntimeError("Error al restaurar el usuario")

    def get_all_empresas(self) -> list[EmpresasExternasToa]:
        """
        Get all empresas for dropdown selection.

        Returns:
            List of all EmpresasExternasToa instances
        """
        return EmpresasExternasToa.query.all()
