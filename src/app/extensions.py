from flask import Flask

from src.services.empresas_externas_service import EmpresasExternasService
from src.services.historia_iniciados_service import HistoriaIniciadosService
from src.use_cases.empresas.empresas_externas_use_case import \
    EmpresasExternasUseCase
from src.use_cases.historia_ot.historia_iniciados_use_case import \
    HistoriaIniciadosUseCase


class Services:
    """Flask extension for managing application services."""

    def __init__(self, app: Flask | None = None):
        self.historia_iniciados: HistoriaIniciadosService | None = None
        self.empresas_externas: EmpresasExternasService | None = None
        self.historia_iniciados_use_case: HistoriaIniciadosUseCase | None = None
        self.empresas_externas_use_case: EmpresasExternasUseCase | None = None
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

        # Initialize use cases with dependencies
        self.historia_iniciados_use_case = HistoriaIniciadosUseCase(
            self.historia_iniciados, self.empresas_externas
        )
        self.empresas_externas_use_case = EmpresasExternasUseCase(
            self.empresas_externas
        )

        app.extensions["services"] = self
        self._initialized = True
        print("TOA services initialized successfully")


# Global services instance
services = Services()
