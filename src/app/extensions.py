from flask import Flask
from flask_login import LoginManager

from src.services.comentarios_service import ComentariosService
from src.services.empresas_externas_service import EmpresasExternasService
from src.services.historia_iniciados_service import HistoriaIniciadosService
from src.services.orden_trabajo_service import OrdenTrabajoService
from src.services.tecnico_supervisor_service import TecnicoSupervisorService
from src.use_cases.comentarios.comentarios_use_case import ComentariosUseCase
from src.use_cases.empresas.empresas_externas_use_case import EmpresasExternasUseCase
from src.use_cases.historia_ot.historia_iniciados_use_case import (
    HistoriaIniciadosUseCase,
)
from src.use_cases.orden_trabajo.orden_trabajo_use_case import OrdenTrabajoUseCase
from src.use_cases.tecnicos.tecnico_supervisor_use_case import TecnicoSupervisorUseCase


class Services:
    """Flask extension for managing application services."""

    def __init__(self, app: Flask | None = None):
        self.historia_iniciados: HistoriaIniciadosService | None = None
        self.empresas_externas: EmpresasExternasService | None = None
        self.orden_trabajo: OrdenTrabajoService | None = None
        self.comentarios: ComentariosService | None = None
        self.tecnico_supervisor: TecnicoSupervisorService | None = None
        self.historia_iniciados_use_case: HistoriaIniciadosUseCase | None = None
        self.empresas_externas_use_case: EmpresasExternasUseCase | None = None
        self.orden_trabajo_use_case: OrdenTrabajoUseCase | None = None
        self.comentarios_use_case: ComentariosUseCase | None = None
        self.tecnico_supervisor_use_case: TecnicoSupervisorUseCase | None = None
        self._initialized = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize services with the Flask app."""
        if self._initialized:
            print("Services already initialized, skipping...")
            return

        print("Initializing TOA services...")

        # Initialize core services
        self.historia_iniciados = HistoriaIniciadosService()
        self.empresas_externas = EmpresasExternasService()
        self.orden_trabajo = OrdenTrabajoService()
        self.comentarios = ComentariosService()
        self.tecnico_supervisor = TecnicoSupervisorService()

        # Initialize use cases with dependencies
        self.historia_iniciados_use_case = HistoriaIniciadosUseCase(
            self.historia_iniciados, self.empresas_externas
        )
        self.empresas_externas_use_case = EmpresasExternasUseCase(
            self.empresas_externas
        )
        self.orden_trabajo_use_case = OrdenTrabajoUseCase(
            self.orden_trabajo, self.empresas_externas
        )
        self.comentarios_use_case = ComentariosUseCase(
            self.comentarios, self.orden_trabajo
        )
        self.tecnico_supervisor_use_case = TecnicoSupervisorUseCase(
            self.tecnico_supervisor
        )

        app.extensions["services"] = self
        self._initialized = True
        print("TOA services initialized successfully")


# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    from src.models.auth.user import User
    return User.query.get(int(user_id))


# Global services instance
services = Services()
