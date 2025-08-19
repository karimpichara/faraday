"""
Pytest configuration and shared fixtures for testing.
"""

from unittest.mock import Mock

import pytest

from src.services.empresas_externas_service import EmpresasExternasService
from src.services.historia_iniciados_service import HistoriaIniciadosService
from src.use_cases.historia_ot.historia_iniciados_use_case import HistoriaIniciadosUseCase


class MockEmpresa:
    """Mock empresa object to simulate SQLAlchemy model behavior"""

    def __init__(self, nombre_toa: str):
        self.nombre_toa = nombre_toa


@pytest.fixture
def mock_empresas_externas_service():
    """Mock empresas externas service with predefined test data"""
    service = Mock(spec=EmpresasExternasService)

    # Default test empresas
    test_empresas = [
        MockEmpresa("EMPRESA_TEST_A"),
        MockEmpresa("EMPRESA_TEST_B"),
        MockEmpresa("EMPRESA_TEST_C"),
        MockEmpresa("TECNICOS_SUR"),
        MockEmpresa("NORTE_CORP"),
    ]

    service.get_empresas_externas_toa_all.return_value = test_empresas
    service.set_empresas_externas_toa.return_value = True

    return service


@pytest.fixture
def mock_historia_iniciados_service():
    """Mock historia iniciados service"""
    service = Mock(spec=HistoriaIniciadosService)
    service.set_data_to_database.return_value = None
    return service


@pytest.fixture
def historia_iniciados_use_case(
    mock_empresas_externas_service, mock_historia_iniciados_service
):
    """Create HistoriaIniciadosUseCase instance with mocked dependencies"""
    return HistoriaIniciadosUseCase(
        historia_iniciados_service=mock_historia_iniciados_service,
        empresas_externas_service=mock_empresas_externas_service,
    )


@pytest.fixture
def sample_ot_data():
    """Sample OT data for testing"""
    return [
        {
            "Técnico": "Juan EMPRESA_TEST_A Rodriguez",
            "OT": "OT-001",
            "Fecha": "2024-01-15",
        },
        {
            "Técnico": "Maria EMPRESA_TEST_B Lopez",
            "OT": "OT-002",
            "Fecha": "2024-01-16",
        },
        {
            "Técnico": "Carlos TECNICOS_SUR Martinez",
            "OT": "OT-003",
            "Fecha": "2024-01-17",
        },
        {"Técnico": "Ana NORTE_CORP Gonzalez", "OT": "OT-004", "Fecha": "2024-01-18"},
        {
            "Técnico": "Pedro EMPRESA_DESCONOCIDA Silva",
            "OT": "OT-005",
            "Fecha": "2024-01-19",
        },
    ]


@pytest.fixture
def empty_ot_data():
    """Empty OT data for edge case testing"""
    return []


@pytest.fixture
def malformed_ot_data():
    """Malformed OT data for error testing"""
    return [
        {"Técnico": "Juan Test", "OT": "OT-001"},  # Valid
        {"OT": "OT-002"},  # Missing Técnico
        {"Técnico": "", "OT": "OT-003"},  # Empty Técnico
        {},  # Empty dict
        {"Técnico": None, "OT": "OT-004"},  # None Técnico
    ]
