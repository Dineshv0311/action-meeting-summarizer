from flask import Blueprint, request, jsonify
from app.api.middlewares import validate_and_save_audio
from app.container import container
from app.core.exceptions import AppException

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

@api_v1_bp.route("/transcribe", methods=["POST"])
def transcribe_meeting():
    if "audio" not in request.files:
        return jsonify({"error": "Missing multipart form field 'audio'"}), 400

    uploaded_file = request.files["audio"]
    file_path = validate_and_save_audio(uploaded_file)
    result = container.meeting_service.process_transcription(file_path)

    return jsonify({
        "status": "success",
        "data": result.model_dump()
    }), 200

@api_v1_bp.route("/meetings/process", methods=["POST"])
def process_full_meeting():
    """Upload audio -> Transcribe -> Structured Summary + Action Items."""
    if "audio" not in request.files:
        return jsonify({"error": "Missing multipart form field 'audio'"}), 400

    uploaded_file = request.files["audio"]
    file_path = validate_and_save_audio(uploaded_file)
    result = container.meeting_service.process_meeting_pipeline(file_path)

    return jsonify({
        "status": "success",
        "data": result.model_dump()
    }), 200

@api_v1_bp.app_errorhandler(AppException)
def handle_app_exception(error: AppException):
    return jsonify({"error": error.message}), error.status_code

@api_v1_bp.app_errorhandler(413)
def handle_file_too_large(error):
    return jsonify({"error": "File size exceeds the configured maximum limit."}), 413