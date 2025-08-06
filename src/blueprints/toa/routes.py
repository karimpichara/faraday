from flask import Blueprint, jsonify, request

from src.services.empresas_externas_service import EmpresasExternasService
from src.services.historia_iniciados_service import HistoriaIniciadosService
from use_cases.empresas.empresas_externas_use_case import EmpresasExternasUseCase
from use_cases.historia_ot.historia_iniciados_use_case import HistoriaIniciadosUseCase

toa_bp = Blueprint("toa", __name__, url_prefix="/toa")


@toa_bp.route("/healthcheck")
def healthcheck():
    return jsonify({"status": "ok"})


@toa_bp.route("/set_data_toa_historia_south_zone", methods=["POST"])
def set_data_toa_historia_south_zone():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"error": "File must be a JSON file"}), 400

        historia_iniciados_service = HistoriaIniciadosService()
        empresas_externas_service = EmpresasExternasService()
        historia_iniciados_use_case = HistoriaIniciadosUseCase(
            historia_iniciados_service, empresas_externas_service
        )
        ot_no_ingresadas = historia_iniciados_use_case.set_data_zona_sur(file)
        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "No ingresadas": ot_no_ingresadas,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@toa_bp.route("/set_data_toa_historia_north_zone", methods=["POST"])
def set_data_toa_historia_north_zone():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"error": "File must be a JSON file"}), 400

        historia_iniciados_service = HistoriaIniciadosService()
        empresas_externas_service = EmpresasExternasService()
        historia_iniciados_use_case = HistoriaIniciadosUseCase(
            historia_iniciados_service, empresas_externas_service
        )
        ot_no_ingresadas = historia_iniciados_use_case.set_data_zona_norte(file)
        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "No ingresadas": ot_no_ingresadas,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@toa_bp.route("/set_data_toa_historia_center_zone", methods=["POST"])
def set_data_toa_historia_center_zone():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if not file.filename.endswith(".json"):
            return jsonify({"error": "File must be a JSON file"}), 400

        historia_iniciados_service = HistoriaIniciadosService()
        empresas_externas_service = EmpresasExternasService()
        historia_iniciados_use_case = HistoriaIniciadosUseCase(
            historia_iniciados_service, empresas_externas_service
        )
        ot_no_ingresadas = historia_iniciados_use_case.set_data_zona_centro(file)
        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "No ingresadas": ot_no_ingresadas,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@toa_bp.route("/set_data_toa_historia_metro_zone", methods=["POST"])
def set_data_toa_historia_metropolitana_zone():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if not file.filename.endswith(".json"):
            return jsonify({"error": "File must be a JSON file"}), 400

        historia_iniciados_service = HistoriaIniciadosService()
        empresas_externas_service = EmpresasExternasService()
        historia_iniciados_use_case = HistoriaIniciadosUseCase(
            historia_iniciados_service, empresas_externas_service
        )
        ot_no_ingresadas = historia_iniciados_use_case.set_data_zona_metropolitana(file)
        return (
            jsonify(
                {
                    "message": "File uploaded successfully",
                    "No ingresadas": ot_no_ingresadas,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@toa_bp.route("/set_empresas_externas_toa", methods=["POST"])
def set_empresas_externas_toa():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
        if not file.filename.endswith(".json"):
            return jsonify({"error": "File must be a JSON file"}), 400

        empresas_externas_service = EmpresasExternasService()
        empresas_externas_use_case = EmpresasExternasUseCase(empresas_externas_service)
        empresas_externas_use_case.set_empresas_externas_toa(file)
        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
