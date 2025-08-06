from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"autocommit": False})
migrate = Migrate()

# Import base models first to avoid circular imports
from src.models.base import BaseModel  # noqa: E402

# Import other models
from src.models.empresas_externas_toa import EmpresasExternasToa  # noqa: E402
from src.models.historia_ot_empresas import HistoriaOtEmpresas  # noqa: E402
from src.models.orden_trabajo import OrdenTrabajo  # noqa: E402
from src.models.comentarios import Comentario  # noqa: E402
from src.models.auth.user import User, Role, UserRole  # noqa: E402

__all__ = [
    "db",
    "migrate",
    "BaseModel",
    "EmpresasExternasToa",
    "HistoriaOtEmpresas",
    "OrdenTrabajo",
    "User",
    "Role",
    "UserRole",
    "Comentario",
]
