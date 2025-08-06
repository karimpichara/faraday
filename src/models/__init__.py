from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={"autocommit": False})
migrate = Migrate()

from src.models.empresas_externas_toa import EmpresasExternasToa  # noqa: E402
from src.models.historia_ot_empresas import HistoriaOtEmpresas  # noqa: E402

__all__ = ["db", "migrate", "EmpresasExternasToa", "HistoriaOtEmpresas"]
